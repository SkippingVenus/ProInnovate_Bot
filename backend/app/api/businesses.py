from typing import Optional
from pydantic import BaseModel, EmailStr

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_business, require_active_subscription
from app.models.business import Business
from app.services.ai_service import build_system_prompt

router = APIRouter(prefix="/api/businesses", tags=["businesses"])


class OnboardingRequest(BaseModel):
    """Datos del formulario de onboarding del negocio."""
    nombre: str
    rubro: str
    tono: str  # cercano / profesional / divertido
    descripcion: Optional[str] = None
    publico_objetivo: Optional[str] = None
    horario: Optional[str] = None
    whatsapp: Optional[str] = None


class BusinessResponse(BaseModel):
    id: int
    nombre: str
    rubro: str
    tono: str
    descripcion: Optional[str]
    publico_objetivo: Optional[str]
    horario: Optional[str]
    whatsapp: Optional[str]
    fb_page_id: Optional[str]
    fb_page_name: Optional[str]
    ig_account_id: Optional[str]
    gmb_location_id: Optional[str]
    plan: str
    email: str

    model_config = {"from_attributes": True}


class ConnectionStatus(BaseModel):
    facebook: bool
    instagram: bool
    google: bool


@router.get("/me", response_model=BusinessResponse)
def get_my_business(business: Business = Depends(get_current_business)):
    """Devuelve el perfil del negocio autenticado."""
    return business


@router.post("/onboarding", response_model=BusinessResponse)
def complete_onboarding(
    payload: OnboardingRequest,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    """Completa el onboarding del negocio y genera el system prompt del agente IA."""
    valid_tonos = {"cercano", "profesional", "divertido"}
    if payload.tono not in valid_tonos:
        raise HTTPException(
            status_code=400,
            detail=f"Tono inválido. Debe ser uno de: {', '.join(valid_tonos)}",
        )

    business.nombre = payload.nombre
    business.rubro = payload.rubro
    business.tono = payload.tono
    business.descripcion = payload.descripcion
    business.publico_objetivo = payload.publico_objetivo
    business.horario = payload.horario
    business.whatsapp = payload.whatsapp

    # Generar y guardar el system prompt personalizado para el agente IA
    business.system_prompt = build_system_prompt(payload.model_dump())

    db.commit()
    db.refresh(business)
    return business


@router.put("/me", response_model=BusinessResponse)
def update_business(
    payload: OnboardingRequest,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    """Actualiza los datos del negocio y regenera el system prompt."""
    return complete_onboarding(payload, db, business)


@router.get("/me/connections", response_model=ConnectionStatus)
def get_connection_status(business: Business = Depends(get_current_business)):
    """Devuelve el estado de las conexiones OAuth."""
    return ConnectionStatus(
        facebook=bool(business.fb_access_token),
        instagram=bool(business.ig_account_id and business.fb_access_token),
        google=bool(business.gmb_access_token),
    )


@router.put("/me/gmb-location")
def set_gmb_location(
    location_id: str,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    """Configura el ID de ubicación de Google My Business."""
    business.gmb_location_id = location_id
    db.commit()
    return {"detail": "Ubicación de Google My Business configurada."}


@router.put("/me/fb-page")
def set_fb_page(
    page_id: str,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    """Configura el ID de la página de Facebook."""
    business.fb_page_id = page_id
    db.commit()
    return {"detail": "Página de Facebook configurada."}
