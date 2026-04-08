from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Business(Base):
    """Negocio / cliente de RepuBot."""

    __tablename__ = "negocios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    rubro: Mapped[str] = mapped_column(String(100), nullable=False)
    tono: Mapped[str] = mapped_column(String(50), default="profesional")  # cercano/profesional/divertido
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publico_objetivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    horario: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    whatsapp: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Credenciales OAuth (cifradas con Fernet)
    fb_page_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fb_page_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    fb_access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ig_account_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ig_access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gmb_location_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    gmb_access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Prompt del agente IA
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Autenticación del dueño
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)

    # Suscripción
    plan: Mapped[str] = mapped_column(String(20), default="basico")  # basico/pro/agencia
    suscripcion_vence: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
