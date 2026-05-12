from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


MetricPlatform = Literal["fb", "ig", "gmaps"]


class MetricCreate(BaseModel):
    negocio_id: UUID
    plataforma: MetricPlatform
    fecha: date
    seguidores: Optional[int] = None
    alcance_organico: Optional[int] = None
    mensajes_recibidos: int = 0
    mensajes_respondidos: int = 0
    resenas_positivas: int = 0
    resenas_negativas: int = 0
    rating_promedio: Optional[float] = None
    posts_publicados: int = 0


class MetricRead(MetricCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MetricUpdate(BaseModel):
    plataforma: Optional[MetricPlatform] = None
    fecha: Optional[date] = None
    seguidores: Optional[int] = None
    alcance_organico: Optional[int] = None
    mensajes_recibidos: Optional[int] = None
    mensajes_respondidos: Optional[int] = None
    resenas_positivas: Optional[int] = None
    resenas_negativas: Optional[int] = None
    rating_promedio: Optional[float] = None
    posts_publicados: Optional[int] = None