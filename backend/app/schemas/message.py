from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


MessagePlatform = Literal["fb", "ig", "gmaps"]
MessageType = Literal["comentario", "dm", "resena"]
MessageState = Literal["pendiente", "aprobado", "enviado", "ignorado"]
ResponseQuality = Literal["aprobada_directa", "aprobada_editada", "ignorada"]


class MessageCreate(BaseModel):
    negocio_id: UUID
    plataforma: MessagePlatform
    tipo: MessageType
    autor: Optional[str] = None
    contenido_original: str
    respuesta_sugerida: Optional[str] = None
    respuesta_enviada: Optional[str] = None
    respuesta_editada_por_dueno: bool = False
    calidad_respuesta: Optional[ResponseQuality] = None
    estado: MessageState = "pendiente"
    urgente: bool = False
    respondido_at: Optional[datetime] = None


class MessageRead(MessageCreate):
    id: UUID
    created_at: datetime
    autor_id: Optional[str] = None
    external_id: Optional[str] = None
    urgencia: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class MessageUpdate(BaseModel):
    plataforma: Optional[MessagePlatform] = None
    tipo: Optional[MessageType] = None
    autor: Optional[str] = None
    contenido_original: Optional[str] = None
    respuesta_sugerida: Optional[str] = None
    respuesta_enviada: Optional[str] = None
    respuesta_editada_por_dueno: Optional[bool] = None
    calidad_respuesta: Optional[ResponseQuality] = None
    estado: Optional[MessageState] = None
    urgente: Optional[bool] = None
    respondido_at: Optional[datetime] = None