from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_business, require_active_subscription
from app.models.business import Business
from app.models.message import Message
from app.services.ai_service import classify_and_respond, generate_alternative_response
from app.services.meta_service import (
    get_page_comments,
    get_instagram_comments,
    get_messenger_messages,
    get_instagram_direct_messages,
    reply_to_comment,
    reply_to_direct_message,
)
from app.services.gmb_service import get_gmb_reviews, reply_to_review
from app.core.encryption import decrypt_token

router = APIRouter(prefix="/api/messages", tags=["messages"])


class MessageResponse(BaseModel):
    id: int
    plataforma: str
    tipo: Optional[str]
    autor: Optional[str]
    contenido_original: str
    respuesta_sugerida: Optional[str]
    respuesta_enviada: Optional[str]
    estado: str
    urgente: bool
    urgencia: Optional[str]
    created_at: datetime
    respondido_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ApproveRequest(BaseModel):
    respuesta: Optional[str] = None  # Si None, usa la sugerida


class ActionResponse(BaseModel):
    detail: str
    message_id: int


class ReplyRequest(BaseModel):
    respuesta: str


class BulkReplyRequest(BaseModel):
    message_ids: list[int]
    respuesta: str


def _validate_negocio_scope(negocio_id: Optional[int], business: Business) -> None:
    """Evita que un usuario consulte mensajes Meta de otro negocio."""
    if negocio_id is not None and negocio_id != business.id:
        raise HTTPException(status_code=403, detail="No autorizado para este negocio.")


@router.get("/facebook")
async def get_facebook_messages(
    negocio_id: Optional[int] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    business: Business = Depends(require_active_subscription),
):
    """Obtiene comentarios de Facebook para el negocio conectado."""
    _validate_negocio_scope(negocio_id, business)
    if not business.fb_access_token or not business.fb_page_id:
        raise HTTPException(status_code=400, detail="Conexión de Facebook incompleta.")

    fb_token = decrypt_token(business.fb_access_token)
    comments = await get_page_comments(fb_token, business.fb_page_id, limit=limit)
    return {"items": comments, "count": len(comments)}


@router.get("/instagram")
async def get_instagram_messages(
    negocio_id: Optional[int] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    business: Business = Depends(require_active_subscription),
):
    """Obtiene comentarios de Instagram para el negocio conectado."""
    _validate_negocio_scope(negocio_id, business)
    if not business.ig_account_id:
        raise HTTPException(status_code=400, detail="Cuenta de Instagram no conectada.")

    token_encrypted = business.ig_access_token or business.fb_access_token
    if not token_encrypted:
        raise HTTPException(status_code=400, detail="Token de Instagram no configurado.")

    ig_token = decrypt_token(token_encrypted)
    comments = await get_instagram_comments(ig_token, business.ig_account_id, limit=limit)
    return {"items": comments, "count": len(comments)}


@router.get("/messenger")
async def get_messenger_direct_messages(
    negocio_id: Optional[int] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    business: Business = Depends(require_active_subscription),
):
    """Obtiene mensajes directos de Messenger."""
    _validate_negocio_scope(negocio_id, business)
    if not business.fb_access_token or not business.fb_page_id:
        raise HTTPException(status_code=400, detail="Conexión de Messenger incompleta.")

    fb_token = decrypt_token(business.fb_access_token)
    messages = await get_messenger_messages(fb_token, business.fb_page_id, limit=limit)
    return {"items": messages, "count": len(messages)}


@router.get("/instagram/direct")
async def get_instagram_direct(
    negocio_id: Optional[int] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    business: Business = Depends(require_active_subscription),
):
    """Obtiene mensajes directos de Instagram."""
    _validate_negocio_scope(negocio_id, business)
    if not business.ig_account_id:
        raise HTTPException(status_code=400, detail="Cuenta de Instagram no conectada.")

    token_encrypted = business.ig_access_token or business.fb_access_token
    if not token_encrypted:
        raise HTTPException(status_code=400, detail="Token de Instagram no configurado.")

    ig_token = decrypt_token(token_encrypted)
    messages = await get_instagram_direct_messages(ig_token, business.ig_account_id, limit=limit)
    return {"items": messages, "count": len(messages)}


@router.get("/", response_model=List[MessageResponse])
def list_messages(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    plataforma: Optional[str] = Query(None),
    urgente: Optional[bool] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    business: Business = Depends(require_active_subscription),
):
    """Lista mensajes de la bandeja unificada, ordenados por urgencia y fecha."""
    query = db.query(Message).filter(Message.negocio_id == business.id)
    if estado:
        query = query.filter(Message.estado == estado)
    if plataforma:
        query = query.filter(Message.plataforma == plataforma)
    if urgente is not None:
        query = query.filter(Message.urgente == urgente)

    # Ordenar: urgentes primero, luego por fecha descendente
    query = query.order_by(Message.urgente.desc(), Message.created_at.desc())
    return query.offset(skip).limit(limit).all()


@router.post("/sync")
async def sync_messages(
    db: Session = Depends(get_db),
    business: Business = Depends(require_active_subscription),
):
    """
    Sincroniza mensajes de todas las plataformas conectadas, los clasifica con IA
    y los guarda en la bandeja unificada.
    """
    system_prompt = business.system_prompt or ""
    nuevos = 0

    # ── Facebook ────────────────────────────────────────────────────────────
    if business.fb_access_token and business.fb_page_id:
        fb_token = decrypt_token(business.fb_access_token)
        comments = await get_page_comments(fb_token, business.fb_page_id)
        for comment in comments:
            ext_id = comment.get("id")
            if db.query(Message).filter(
                Message.negocio_id == business.id,
                Message.external_id == ext_id,
            ).first():
                continue  # Ya procesado
            ai_result = classify_and_respond(
                comment.get("message", ""), system_prompt, "Facebook"
            )
            msg = Message(
                negocio_id=business.id,
                plataforma="facebook",
                tipo=ai_result.get("tipo"),
                autor=comment.get("from", {}).get("name"),
                contenido_original=comment.get("message", ""),
                respuesta_sugerida=ai_result.get("respuesta_sugerida"),
                urgencia=ai_result.get("urgencia"),
                urgente=ai_result.get("urgente", False),
                external_id=ext_id,
            )
            db.add(msg)
            nuevos += 1

    # ── Instagram ───────────────────────────────────────────────────────────
    if business.fb_access_token and business.ig_account_id:
        ig_token = decrypt_token(business.fb_access_token)
        ig_comments = await get_instagram_comments(ig_token, business.ig_account_id)
        for comment in ig_comments:
            ext_id = comment.get("id")
            if db.query(Message).filter(
                Message.negocio_id == business.id,
                Message.external_id == ext_id,
            ).first():
                continue
            ai_result = classify_and_respond(
                comment.get("text", ""), system_prompt, "Instagram"
            )
            msg = Message(
                negocio_id=business.id,
                plataforma="instagram",
                tipo=ai_result.get("tipo"),
                autor=comment.get("username"),
                contenido_original=comment.get("text", ""),
                respuesta_sugerida=ai_result.get("respuesta_sugerida"),
                urgencia=ai_result.get("urgencia"),
                urgente=ai_result.get("urgente", False),
                external_id=ext_id,
            )
            db.add(msg)
            nuevos += 1

    # ── Google My Business ──────────────────────────────────────────────────
    if business.gmb_access_token and business.gmb_location_id:
        gmb_token = decrypt_token(business.gmb_access_token)
        reviews = await get_gmb_reviews(gmb_token, business.gmb_location_id)
        for review in reviews:
            ext_id = review.get("reviewId") or review.get("name")
            if db.query(Message).filter(
                Message.negocio_id == business.id,
                Message.external_id == ext_id,
            ).first():
                continue
            contenido = review.get("comment", "")
            rating = review.get("starRating", "")
            ai_result = classify_and_respond(
                f"[Reseña Google - {rating} estrellas]: {contenido}",
                system_prompt,
                "Google Maps",
            )
            msg = Message(
                negocio_id=business.id,
                plataforma="google",
                tipo=ai_result.get("tipo"),
                autor=review.get("reviewer", {}).get("displayName"),
                contenido_original=contenido,
                respuesta_sugerida=ai_result.get("respuesta_sugerida"),
                urgencia=ai_result.get("urgencia"),
                urgente=ai_result.get("urgente", False),
                external_id=ext_id,
            )
            db.add(msg)
            nuevos += 1

    db.commit()
    return {"detail": f"Sincronización completada. {nuevos} mensajes nuevos procesados."}


@router.post("/{message_id}/approve", response_model=ActionResponse)
async def approve_message(
    message_id: int,
    payload: ApproveRequest,
    db: Session = Depends(get_db),
    business: Business = Depends(require_active_subscription),
):
    """Aprueba y publica la respuesta a un mensaje."""
    msg = _get_message(db, message_id, business.id)
    respuesta = payload.respuesta or msg.respuesta_sugerida
    if not respuesta:
        raise HTTPException(status_code=400, detail="No hay respuesta para publicar.")

    # Publicar según la plataforma
    published = False
    if msg.plataforma in ("facebook", "instagram") and business.fb_access_token:
        fb_token = decrypt_token(business.fb_access_token)
        result = await reply_to_comment(fb_token, msg.external_id, respuesta)
        published = result is not None
    elif msg.plataforma == "google" and business.gmb_access_token and business.gmb_location_id:
        gmb_token = decrypt_token(business.gmb_access_token)
        result = await reply_to_review(
            gmb_token, business.gmb_location_id, msg.external_id, respuesta
        )
        published = result is not None
    else:
        # Sin token configurado: marcar como aprobado sin publicar
        published = True

    msg.respuesta_enviada = respuesta
    msg.estado = "enviado" if published else "aprobado"
    msg.respondido_at = datetime.utcnow()
    db.commit()
    return ActionResponse(detail="Respuesta publicada exitosamente.", message_id=message_id)


@router.post("/{message_id}/reply", response_model=ActionResponse)
async def reply_message(
    message_id: int,
    payload: ReplyRequest,
    db: Session = Depends(get_db),
    business: Business = Depends(require_active_subscription),
):
    """Publica una respuesta individual para comentarios/DMs de Meta."""
    msg = _get_message(db, message_id, business.id)
    respuesta = payload.respuesta.strip()
    if not respuesta:
        raise HTTPException(status_code=400, detail="La respuesta no puede estar vacía.")

    if not business.fb_access_token:
        raise HTTPException(status_code=400, detail="Token de Meta no configurado.")

    fb_token = decrypt_token(business.fb_access_token)
    published = False

    if msg.plataforma in ("facebook", "instagram"):
        result = await reply_to_comment(fb_token, msg.external_id, respuesta)
        published = result is not None
    elif msg.plataforma in ("messenger", "instagram_direct"):
        recipient_id = msg.autor_id or msg.external_id
        result = await reply_to_direct_message(fb_token, recipient_id, respuesta)
        published = result is not None

    if not published:
        raise HTTPException(status_code=502, detail="No se pudo enviar la respuesta a Meta.")

    msg.respuesta_enviada = respuesta
    msg.estado = "enviado"
    msg.respondido_at = datetime.utcnow()
    db.commit()
    return ActionResponse(detail="Respuesta publicada exitosamente.", message_id=message_id)


@router.post("/bulk-reply")
async def bulk_reply_messages(
    payload: BulkReplyRequest,
    db: Session = Depends(get_db),
    business: Business = Depends(require_active_subscription),
):
    """Publica la misma respuesta en múltiples mensajes del negocio."""
    sent: list[int] = []
    failed: list[int] = []

    for message_id in payload.message_ids:
        msg = db.query(Message).filter(
            Message.id == message_id,
            Message.negocio_id == business.id,
        ).first()
        if not msg:
            failed.append(message_id)
            continue

        try:
            await reply_message(
                message_id=message_id,
                payload=ReplyRequest(respuesta=payload.respuesta),
                db=db,
                business=business,
            )
            sent.append(message_id)
        except HTTPException:
            failed.append(message_id)

    return {
        "detail": "Respuestas masivas procesadas.",
        "enviados": sent,
        "fallidos": failed,
    }


@router.post("/{message_id}/ignore", response_model=ActionResponse)
def ignore_message(
    message_id: int,
    db: Session = Depends(get_db),
    business: Business = Depends(require_active_subscription),
):
    """Marca un mensaje como ignorado."""
    msg = _get_message(db, message_id, business.id)
    msg.estado = "ignorado"
    db.commit()
    return ActionResponse(detail="Mensaje ignorado.", message_id=message_id)


@router.post("/{message_id}/regenerate", response_model=ActionResponse)
def regenerate_response(
    message_id: int,
    db: Session = Depends(get_db),
    business: Business = Depends(require_active_subscription),
):
    """Solicita una respuesta alternativa para el mensaje."""
    msg = _get_message(db, message_id, business.id)
    system_prompt = business.system_prompt or ""
    nueva_respuesta = generate_alternative_response(
        msg.contenido_original, system_prompt, msg.respuesta_sugerida
    )
    msg.respuesta_sugerida = nueva_respuesta
    db.commit()
    return ActionResponse(
        detail="Nueva respuesta generada.", message_id=message_id
    )


def _get_message(db: Session, message_id: int, negocio_id: int) -> Message:
    """Obtiene un mensaje verificando que pertenece al negocio autenticado."""
    msg = db.query(Message).filter(
        Message.id == message_id,
        Message.negocio_id == negocio_id,
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado.")
    return msg
