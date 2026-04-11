from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Competitor(Base):
    """Competidor monitoreado por el negocio."""

    __tablename__ = "competidores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    negocio_id: Mapped[int] = mapped_column(ForeignKey("negocios.id"), nullable=False, index=True)

    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    fb_page_url: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    ig_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    gmb_place_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    ultimo_analisis: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    negocio = relationship("Business", backref="competidores")
