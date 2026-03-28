from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Message(Base):
    """Mensaje/comentario/reseña recibido en alguna plataforma."""

    __tablename__ = "mensajes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    negocio_id: Mapped[int] = mapped_column(ForeignKey("negocios.id"), nullable=False, index=True)

    # Origen
    plataforma: Mapped[str] = mapped_column(String(30), nullable=False)  # facebook/instagram/google
    tipo: Mapped[str] = mapped_column(String(20), nullable=True)  # consulta/queja/elogio/spam
    autor: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contenido_original: Mapped[str] = mapped_column(Text, nullable=False)

    # Respuestas
    respuesta_sugerida: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    respuesta_enviada: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Estado: pendiente / aprobado / enviado / ignorado
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    urgente: Mapped[bool] = mapped_column(Boolean, default=False)

    # Urgencia clasificada por IA: alta / media / baja
    urgencia: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # ID externo de la plataforma (para publicar la respuesta)
    external_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    respondido_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    negocio = relationship("Business", backref="mensajes")
