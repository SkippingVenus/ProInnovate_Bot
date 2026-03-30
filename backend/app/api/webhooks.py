import hmac
import hashlib
import json
import logging

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import get_settings
from app.services.culqi_service import process_culqi_charge, verify_culqi_signature

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post("/culqi")
async def culqi_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook de Culqi para procesar pagos y actualizar suscripciones.
    Verifica la firma HMAC antes de procesar el evento.
    """
    body = await request.body()
    signature = request.headers.get("x-culqi-signature", "")

    if settings.CULQI_WEBHOOK_SECRET and not verify_culqi_signature(body, signature):
        logger.warning("Firma inválida en webhook de Culqi")
        raise HTTPException(status_code=400, detail="Firma de webhook inválida.")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Payload JSON inválido.")

    event_type = payload.get("type", "")
    logger.info("Evento Culqi recibido: %s", event_type)

    # Procesar cargos exitosos
    if event_type in ("charge.succeeded", "charge.created"):
        charge_data = payload.get("data", payload)
        sub = process_culqi_charge(db, charge_data)
        if sub:
            return {"detail": f"Suscripción activada: plan {sub.plan}"}
        return {"detail": "Evento procesado sin acción."}

    return {"detail": f"Evento '{event_type}' recibido pero no procesado."}


@router.post("/meta")
async def meta_webhook_verify(request: Request):
    """
    Endpoint de verificación para el webhook de Meta (Facebook/Instagram).
    Meta envía un GET para verificar y POST para entregar eventos.
    """
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    # Verificación inicial de Meta
    if mode == "subscribe" and token == settings.META_APP_SECRET:
        return int(challenge)

    body = await request.body()
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return {"detail": "Payload recibido."}

    logger.info("Evento Meta webhook recibido: %s", payload.get("object"))
    # Aquí se procesarían los eventos de Meta en tiempo real (DMs, comentarios nuevos)
    return {"detail": "Evento Meta recibido."}
