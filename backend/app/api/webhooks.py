import hmac
import hashlib
import json
import logging
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi import Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import get_settings
from app.services.culqi_service import process_culqi_charge, verify_culqi_signature
from app.models.business import Business
from app.models.message import Message
from app.services.ai_service import classify_and_respond

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
settings = get_settings()
logger = logging.getLogger(__name__)

URGENT_KEYWORDS = (
    "reclamo",
    "queja",
    "indecopi",
    "demanda",
    "devolucion",
    "reembolso",
    "fraude",
    "estafa",
    "urgente",
    "malo",
)


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


@router.get("/meta")
async def meta_webhook_handshake(
    mode: str = Query(alias="hub.mode"),
    token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge"),
):
    """Verificación inicial de webhook solicitada por Meta.
    
    Meta envía:
      hub.mode=subscribe
      hub.verify_token=<token>
      hub.challenge=<challenge>
    
    Responde con 200 + challenge como plain text si es válido, sino 403.
    """
    if mode != "subscribe":
        raise HTTPException(status_code=403, detail="Invalid mode.")

    if token != settings.META_WEBHOOK_VERIFY_TOKEN:
        raise HTTPException(status_code=403, detail="Verify token inválido.")

    # Meta expects the challenge value as plain text
    return Response(content=challenge, media_type="text/plain")


@router.post("/meta")
async def meta_webhook_events(request: Request, db: Session = Depends(get_db)):
    """Recibe eventos de Meta en tiempo real y los guarda en la bandeja."""
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")
    if settings.META_APP_SECRET and not _is_valid_meta_signature(body, signature):
        raise HTTPException(status_code=401, detail="Firma de webhook inválida.")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Payload JSON inválido.")

    inserted = 0
    for entry in payload.get("entry", []):
        inserted += _process_meta_entry(payload.get("object", ""), entry, db)

    if inserted:
        db.commit()

    return {"detail": "Evento Meta recibido.", "insertados": inserted}


def _is_valid_meta_signature(body: bytes, signature_header: str) -> bool:
    """Valida X-Hub-Signature-256 con SHA256 y META_APP_SECRET."""
    if not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.META_APP_SECRET.encode("utf-8"),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    received = signature_header.split("=", 1)[1]
    return hmac.compare_digest(expected, received)


def _process_meta_entry(object_type: str, entry: dict, db: Session) -> int:
    """Transforma un entry de Meta en uno o más mensajes almacenables."""
    business = _resolve_business(object_type, entry, db)
    if not business:
        return 0

    inserted = 0
    for record in _extract_events(object_type, entry):
        ext_id = record.get("external_id")
        if not ext_id:
            continue

        exists = db.query(Message).filter(
            Message.plataforma == record["plataforma"],
            Message.external_id == ext_id,
        ).first()
        if exists:
            continue

        text = record.get("contenido_original", "")
        ai_result = _classify_webhook_message(business, text, record["plataforma"], record["tipo"])

        msg = Message(
            negocio_id=business.id,
            plataforma=record["plataforma"],
            tipo=ai_result.get("tipo") or record["tipo"],
            autor=record.get("autor"),
            autor_id=record.get("autor_id"),
            contenido_original=text or "(sin contenido)",
            respuesta_sugerida=ai_result.get("respuesta_sugerida"),
            urgencia=ai_result.get("urgencia"),
            urgente=ai_result.get("urgente", False),
            external_id=ext_id,
        )
        db.add(msg)
        inserted += 1

    return inserted


def _resolve_business(object_type: str, entry: dict, db: Session) -> Optional[Business]:
    """Resuelve el negocio dueño del evento según page/account ID."""
    source_id = entry.get("id")
    if not source_id:
        return None

    if object_type == "instagram":
        return db.query(Business).filter(Business.ig_account_id == source_id).first()

    return db.query(Business).filter(Business.fb_page_id == source_id).first()


def _extract_events(object_type: str, entry: dict) -> list[dict]:
    """Extrae eventos soportados (comentarios y DMs) en una forma uniforme."""
    events: list[dict] = []

    # Formato típico para cambios en feed/comments
    for change in entry.get("changes", []):
        value = change.get("value", {})
        message_text = value.get("message") or value.get("text") or ""
        comment_id = value.get("comment_id") or value.get("id")
        sender = value.get("from", {}) or {}

        if comment_id and message_text:
            events.append(
                {
                    "plataforma": "instagram" if object_type == "instagram" else "facebook",
                    "tipo": "comentario",
                    "external_id": str(comment_id),
                    "autor": sender.get("name") or sender.get("username"),
                    "autor_id": sender.get("id"),
                    "contenido_original": message_text,
                }
            )

    # Formato típico para DMs de Messenger
    for messaging in entry.get("messaging", []):
        sender = messaging.get("sender", {}) or {}
        message_obj = messaging.get("message", {}) or {}
        dm_text = message_obj.get("text", "")
        dm_id = message_obj.get("mid") or messaging.get("timestamp")
        if dm_text and dm_id:
            events.append(
                {
                    "plataforma": "messenger",
                    "tipo": "dm",
                    "external_id": str(dm_id),
                    "autor": sender.get("id"),
                    "autor_id": sender.get("id"),
                    "contenido_original": dm_text,
                }
            )

    return events


def _classify_webhook_message(
    business: Business,
    text: str,
    plataforma: str,
    default_tipo: str,
) -> dict:
    """Clasifica urgencia/tipo usando IA con fallback heurístico."""
    heuristic = _urgent_by_keywords(text)
    fallback = {
        "tipo": default_tipo,
        "urgencia": "alta" if heuristic else "media",
        "respuesta_sugerida": None,
        "urgente": heuristic,
    }

    if not text.strip() or not business.system_prompt:
        return fallback

    try:
        result = classify_and_respond(text, business.system_prompt, plataforma)
        if "urgente" not in result:
            result["urgente"] = result.get("urgencia") == "alta"
        return result
    except Exception:
        return fallback


def _urgent_by_keywords(text: str) -> bool:
    normalized = (text or "").lower()
    return any(keyword in normalized for keyword in URGENT_KEYWORDS)
