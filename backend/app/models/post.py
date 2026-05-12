from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Post(Base):
    """Post generado o publicado para un negocio."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    negocio_id: Mapped[int] = mapped_column(
        ForeignKey("negocios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plataforma: Mapped[str] = mapped_column(String(20), nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    imagen_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tipo_contenido: Mapped[str] = mapped_column(String(50), nullable=False)
    generado_por_ia: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    alcance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    likes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comentarios: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    publicado_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    negocio = relationship("Business", backref="posts")