from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.core.deps import get_current_business
from app.core.config import get_settings
from app.models.business import Business
from app.models.facebook_page import FacebookPage
from app.services.meta_service import (
    get_meta_auth_url,
    exchange_meta_code,
    get_user_pages,
)
from app.services.gmb_service import get_google_auth_url, exchange_google_code
from app.core.encryption import encrypt_token

logger = logging.getLogger(__name__)

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


class ConnectMetaResponse(BaseModel):
    url: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Registra un nuevo negocio en MarkiBot."""
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

@router.get("/meta/login")
def meta_oauth_login():
    """Redirige al usuario a la pantalla de consentimiento OAuth de Meta con los scopes correctos."""
    state = secrets.token_urlsafe(16)
    auth_url = get_meta_auth_url(state)
    return RedirectResponse(url=auth_url)


@router.get("/meta/callback")
async def meta_oauth_callback(
    code: str,
    state: str = Query(default=None),
    db: Session = Depends(get_db),
):
    """Callback OAuth de Meta. Intercambia el código por tokens y guarda todas las páginas de Facebook."""
    try:
        token_data = await exchange_meta_code(code)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error al conectar con Meta: {exc}")

    user_access_token = token_data.get("access_token", "")
    try:
        business_id = int(state) if state else 1
    except (TypeError, ValueError):
        business_id = 1

    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado.")

    # Obtener todas las páginas de Facebook del usuario
    pages = []
    try:
        pages = await get_user_pages(user_access_token)
    except Exception as exc:
        logger.error(f"Error al obtener páginas de Facebook: {exc}")

    if not pages:
        raise HTTPException(status_code=400, detail="No se encontraron páginas de Facebook asociadas a esta cuenta.")

    # Eliminar páginas previas (si existen)
    db.query(FacebookPage).filter(FacebookPage.business_id == business_id).delete()

    # Guardar todas las páginas con tokens encriptados
    saved_pages = []
    for page in pages:
        facebook_page = FacebookPage(
            business_id=business_id,
            fb_page_id=page.get("id"),
            fb_page_name=page.get("name"),
            fb_access_token=encrypt_token(page.get("access_token") or user_access_token),
            instagram_account_id=page.get("instagram_business_account", {}).get("id"),
        )
        db.add(facebook_page)
        saved_pages.append(facebook_page)

    db.commit()

    # Retornar información de las páginas guardadas
    return {
        "detail": "Páginas de Facebook conectadas exitosamente.",
        "pages_count": len(saved_pages),
        "pages": [
            {
                "fb_page_id": p.fb_page_id,
                "fb_page_name": p.fb_page_name,
                "instagram_account_id": p.instagram_account_id,
            }
            for p in saved_pages
        ],
    }


@router.delete("/meta/disconnect/{negocio_id}")
def disconnect_meta(
    negocio_id: int,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    """Desconecta Facebook/Instagram para un negocio autenticado."""
    if business.id != negocio_id:
        raise HTTPException(status_code=403, detail="No autorizado para desconectar este negocio.")

    business.fb_page_id = None
    business.fb_page_name = None
    business.fb_access_token = None
    business.ig_account_id = None
    business.ig_access_token = None
    db.commit()
    return {"detail": "Conexión con Meta eliminada correctamente."}


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
