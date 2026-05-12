from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


SubscriptionPlan = Literal["basico", "pro", "agencia"]
SubscriptionState = Literal["activo", "vencido", "cancelado"]


class SubscriptionCreate(BaseModel):
    negocio_id: UUID
    plan: SubscriptionPlan
    monto_soles: float
    estado: SubscriptionState = "activo"
    fecha_inicio: date
    fecha_vencimiento: date
    culqi_charge_id: Optional[str] = None


class SubscriptionRead(SubscriptionCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SubscriptionUpdate(BaseModel):
    plan: Optional[SubscriptionPlan] = None
    monto_soles: Optional[float] = None
    estado: Optional[SubscriptionState] = None
    fecha_inicio: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    culqi_charge_id: Optional[str] = None