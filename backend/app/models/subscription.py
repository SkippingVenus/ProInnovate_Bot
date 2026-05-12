from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Subscription(Base):
    """Registro de suscripciones y pagos vía Culqi."""

    __tablename__ = "suscripciones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    negocio_id: Mapped[int] = mapped_column(
        ForeignKey("negocios.id", ondelete="CASCADE"), nullable=False, index=True
    )

    plan: Mapped[str] = mapped_column(String(20), nullable=False)  # basico/pro/agencia
    monto_soles: Mapped[float] = mapped_column(Float, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="activo")  # activo/vencido/cancelado

    fecha_inicio: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fecha_vencimiento: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    culqi_charge_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    negocio = relationship("Business", backref="suscripciones")
