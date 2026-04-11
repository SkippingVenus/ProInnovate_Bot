"""Servicio de webhook para Culqi (pasarela de pagos peruana)."""
from __future__ import annotations

import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.business import Business
from app.models.subscription import Subscription

logger = logging.getLogger(__name__)
settings = get_settings()

# Precios de los planes en soles
PLAN_PRECIOS = {
    "basico": 89.0,
    "pro": 179.0,
    "agencia": 399.0,
}


def verify_culqi_signature(payload: bytes, signature: str) -> bool:
    """Verifica la firma HMAC del webhook de Culqi."""
    expected = hmac.new(
        settings.CULQI_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def process_culqi_charge(
    db: Session,
    charge_data: dict,
) -> Optional[Subscription]:
    """
    Procesa un cargo exitoso de Culqi y actualiza la suscripción del negocio.

    El metadata del cargo debe incluir: negocio_id y plan.
    """
    metadata = charge_data.get("metadata", {})
    negocio_id = metadata.get("negocio_id")
    plan = metadata.get("plan", "basico")

    if not negocio_id:
        logger.warning("Webhook Culqi sin negocio_id en metadata: %s", charge_data.get("id"))
        return None

    business = db.query(Business).filter(Business.id == int(negocio_id)).first()
    if not business:
        logger.error("Negocio %s no encontrado al procesar pago Culqi", negocio_id)
        return None

    charge_id = charge_data.get("id", "")
    monto = charge_data.get("amount", 0) / 100.0  # Culqi usa céntimos

    ahora = datetime.utcnow()
    vencimiento = ahora + timedelta(days=30)

    # Crear o actualizar registro de suscripción
    sub = db.query(Subscription).filter(Subscription.culqi_charge_id == charge_id).first()
    if not sub:
        sub = Subscription(
            negocio_id=int(negocio_id),
            plan=plan,
            monto_soles=monto,
            estado="activo",
            fecha_inicio=ahora,
            fecha_vencimiento=vencimiento,
            culqi_charge_id=charge_id,
        )
        db.add(sub)

    # Actualizar el plan y fecha de vencimiento del negocio
    business.plan = plan
    business.suscripcion_vence = vencimiento

    db.commit()
    db.refresh(sub)
    logger.info(
        "Suscripción activada para negocio %s, plan %s, vence %s",
        negocio_id,
        plan,
        vencimiento,
    )
    return sub
