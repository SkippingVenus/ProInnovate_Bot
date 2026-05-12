from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Date, DateTime, Float, Integer, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Metric(Base):
    """Métricas diarias por plataforma para un negocio."""

    __tablename__ = "metricas"
    __table_args__ = (
        UniqueConstraint("negocio_id", "plataforma", "fecha", name="uq_metricas_negocio_plataforma_fecha"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    negocio_id: Mapped[int] = mapped_column(
        ForeignKey("negocios.id", ondelete="CASCADE"), nullable=False, index=True
    )

    plataforma: Mapped[str] = mapped_column(String(30), nullable=False)  # facebook/instagram/google
    fecha: Mapped[date] = mapped_column(Date, nullable=False)

    seguidores: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    alcance_organico: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mensajes_recibidos: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=False)
    mensajes_respondidos: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=False)
    resenas_positivas: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=False)
    resenas_negativas: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=False)
    rating_promedio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    posts_publicados: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    negocio = relationship("Business", backref="metricas")
