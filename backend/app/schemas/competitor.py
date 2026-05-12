from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CompetitorCreate(BaseModel):
    negocio_id: UUID
    nombre: str
    fb_page_url: Optional[str] = None
    ig_username: Optional[str] = None
    gmb_place_id: Optional[str] = None
    ultimo_analisis: Optional[datetime] = None


class CompetitorRead(CompetitorCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CompetitorUpdate(BaseModel):
    nombre: Optional[str] = None
    fb_page_url: Optional[str] = None
    ig_username: Optional[str] = None
    gmb_place_id: Optional[str] = None
    ultimo_analisis: Optional[datetime] = None