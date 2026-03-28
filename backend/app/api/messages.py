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
    reply_to_comment,
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
