from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


BusinessTone = Literal["cercano", "profesional", "divertido"]
BusinessPlan = Literal["basico", "pro", "agencia"]


class BusinessCreate(BaseModel):
    nombre: str
    rubro: str
    tono: BusinessTone
    descripcion: Optional[str] = None
    publico_objetivo: Optional[str] = None
    horario: Optional[str] = None
    whatsapp: Optional[str] = None
    fb_page_id: Optional[str] = None
    ig_account_id: Optional[str] = None
    gmb_location_id: Optional[str] = None
    system_prompt: Optional[str] = None
    plan: BusinessPlan = "basico"
    suscripcion_vence: Optional[datetime] = None


class BusinessRead(BusinessCreate):
    id: UUID
    email: Optional[str] = None
    fb_page_name: Optional[str] = None
    ig_access_token: Optional[str] = None
    gmb_access_token: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BusinessUpdate(BaseModel):
    nombre: Optional[str] = None
    rubro: Optional[str] = None
    tono: Optional[BusinessTone] = None
    descripcion: Optional[str] = None
    publico_objetivo: Optional[str] = None
    horario: Optional[str] = None
    whatsapp: Optional[str] = None
    fb_page_id: Optional[str] = None
    fb_page_name: Optional[str] = None
    fb_access_token: Optional[str] = None
    ig_account_id: Optional[str] = None
    ig_access_token: Optional[str] = None
    gmb_location_id: Optional[str] = None
    gmb_access_token: Optional[str] = None
    system_prompt: Optional[str] = None
    plan: Optional[BusinessPlan] = None
    suscripcion_vence: Optional[datetime] = None