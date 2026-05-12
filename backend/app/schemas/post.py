from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


PostPlatform = Literal["fb", "ig"]
PostContentType = Literal["promo", "detras_de_camaras", "fecha_especial", "agradecimiento", "recordatorio"]


class PostCreate(BaseModel):
    negocio_id: UUID
    plataforma: PostPlatform
    texto: str
    imagen_url: Optional[str] = None
    tipo_contenido: PostContentType
    generado_por_ia: bool = False
    alcance: Optional[int] = None
    likes: Optional[int] = None
    comentarios: Optional[int] = None
    publicado_at: Optional[datetime] = None


class PostRead(PostCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PostUpdate(BaseModel):
    plataforma: Optional[PostPlatform] = None
    texto: Optional[str] = None
    imagen_url: Optional[str] = None
    tipo_contenido: Optional[PostContentType] = None
    generado_por_ia: Optional[bool] = None
    alcance: Optional[int] = None
    likes: Optional[int] = None
    comentarios: Optional[int] = None
    publicado_at: Optional[datetime] = None