from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Date, DateTime, Float, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Metric(Base):
    """Métricas diarias por plataforma para un negocio."""

    __tablename__ = "metricas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    negocio_id: Mapped[int] = mapped_column(ForeignKey("negocios.id"), nullable=False, index=True)

    plataforma: Mapped[str] = mapped_column(String(30), nullable=False)  # facebook/instagram/google
    fecha: Mapped[date] = mapped_column(Date, nullable=False)

    seguidores: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    alcance_organico: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mensajes_recibidos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mensajes_respondidos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resenas_positivas: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resenas_negativas: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rating_promedio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    posts_publicados: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    negocio = relationship("Business", backref="metricas")
