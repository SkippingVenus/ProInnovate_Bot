from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.core.deps import get_current_business
from app.core.config import get_settings
from app.models.business import Business
from app.services.meta_service import get_meta_auth_url, exchange_meta_code
from app.services.gmb_service import get_google_auth_url, exchange_google_code
from app.core.encryption import encrypt_token

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nombre: str
    rubro: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Registra un nuevo negocio en RepuBot."""
    if db.query(Business).filter(Business.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta con ese correo electrónico.",
        )
    business = Business(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        nombre=payload.nombre,
        rubro=payload.rubro,
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    token = create_access_token({"sub": str(business.id)})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Autentica un negocio y devuelve un JWT."""
    business = db.query(Business).filter(Business.email == form_data.username).first()
    if not business or not verify_password(form_data.password, business.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": str(business.id)})
    return TokenResponse(access_token=token)


# ── OAuth Meta ──────────────────────────────────────────────────────────────

@router.get("/meta")
def meta_oauth_start(business: Business = Depends(get_current_business)):
    """Devuelve la URL para iniciar el flujo OAuth con Meta."""
    state = str(business.id)
    return {"url": get_meta_auth_url(state)}


@router.get("/meta/callback")
async def meta_oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """Callback OAuth de Meta. Guarda los tokens cifrados."""
    try:
        token_data = await exchange_meta_code(code)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error al conectar con Meta: {exc}")

    access_token = token_data.get("access_token", "")
    business = db.query(Business).filter(Business.id == int(state)).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado.")

    business.fb_access_token = encrypt_token(access_token)
    db.commit()
    return {"detail": "Facebook/Instagram conectado exitosamente."}


# ── OAuth Google ─────────────────────────────────────────────────────────────

@router.get("/google")
def google_oauth_start(business: Business = Depends(get_current_business)):
    """Devuelve la URL para iniciar el flujo OAuth con Google."""
    state = str(business.id)
    return {"url": get_google_auth_url(state)}


@router.get("/google/callback")
async def google_oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """Callback OAuth de Google. Guarda los tokens cifrados."""
    try:
        token_data = await exchange_google_code(code)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error al conectar con Google: {exc}")

    access_token = token_data.get("access_token", "")
    business = db.query(Business).filter(Business.id == int(state)).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado.")

    business.gmb_access_token = encrypt_token(access_token)
    db.commit()
    return {"detail": "Google My Business conectado exitosamente."}
