"""Conector para Meta Graph API (Facebook Pages + Instagram Business)."""
from __future__ import annotations

import logging
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

META_GRAPH_URL = "https://graph.facebook.com/v19.0"
META_AUTH_URL = "https://www.facebook.com/v19.0/dialog/oauth"
META_TOKEN_URL = "https://graph.facebook.com/v19.0/oauth/access_token"

# Permisos necesarios para el flujo OAuth
META_SCOPES = [
    "pages_show_list",
    "pages_read_engagement",
    "pages_manage_posts",
    "pages_messaging",
    "instagram_basic",
    "instagram_manage_comments",
    "instagram_manage_messages",
]


def get_meta_auth_url(state: str) -> str:
    """Genera la URL de autorización OAuth para Meta."""
    params = {
        "client_id": settings.META_APP_ID,
        "redirect_uri": settings.META_REDIRECT_URI,
        "scope": ",".join(META_SCOPES),
        "response_type": "code",
        "state": state,
    }
    return f"{META_AUTH_URL}?{urlencode(params)}"


async def exchange_meta_code(code: str) -> dict:
    """Intercambia el código de autorización por tokens de acceso."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            META_TOKEN_URL,
            params={
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "redirect_uri": settings.META_REDIRECT_URI,
                "code": code,
            },
        )
        response.raise_for_status()
        return response.json()


async def get_user_pages(user_access_token: str) -> list[dict]:
    """Devuelve páginas de Facebook administradas por el usuario OAuth."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{META_GRAPH_URL}/me/accounts",
                params={
                    "fields": "id,name,access_token,instagram_business_account{id,username}",
                    "access_token": user_access_token,
                },
            )
            logger.debug("Meta /me/accounts raw response: %s", response.text)
            response.raise_for_status()
            payload = response.json()
            if payload.get("error"):
                logger.debug("Meta /me/accounts API error payload: %s", payload.get("error"))
            return payload.get("data", [])
        except httpx.HTTPStatusError as exc:
            logger.debug(
                "Meta /me/accounts HTTP error: status=%s response=%s",
                exc.response.status_code if exc.response else None,
                exc.response.text if exc.response else None,
            )
            raise
        except httpx.RequestError as exc:
            logger.debug("Meta /me/accounts request error: %s", exc)
            raise


async def get_primary_page_connection(user_access_token: str) -> Optional[dict]:
    """Obtiene la mejor conexión disponible (página y cuenta IG asociada)."""
    pages = await get_user_pages(user_access_token)
    if not pages:
        return None

    page = pages[0]
    ig_account = page.get("instagram_business_account") or {}
    return {
        "fb_page_id": page.get("id"),
        "fb_page_name": page.get("name"),
        "fb_access_token": page.get("access_token") or user_access_token,
        "ig_account_id": ig_account.get("id"),
    }


async def get_page_info(page_access_token: str, page_id: str) -> dict:
    """Obtiene información básica de una página de Facebook."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{META_GRAPH_URL}/{page_id}",
            params={"fields": "id,name,fan_count", "access_token": page_access_token},
        )
        response.raise_for_status()
        return response.json()


async def get_page_comments(page_access_token: str, page_id: str, limit: int = 25) -> list[dict]:
    """Obtiene comentarios recientes de publicaciones de la página."""
    try:
        async with httpx.AsyncClient() as client:
            # Obtener publicaciones recientes
            posts_resp = await client.get(
                f"{META_GRAPH_URL}/{page_id}/posts",
                params={
                    "fields": "id,message,created_time",
                    "limit": 10,
                    "access_token": page_access_token,
                },
            )
            posts_resp.raise_for_status()
            posts = posts_resp.json().get("data", [])

            comments: list[dict] = []
            for post in posts[:5]:  # Revisar los 5 posts más recientes
                comm_resp = await client.get(
                    f"{META_GRAPH_URL}/{post['id']}/comments",
                    params={
                        "fields": "id,from,message,created_time",
                        "limit": limit,
                        "access_token": page_access_token,
                    },
                )
                comm_resp.raise_for_status()
                for comment in comm_resp.json().get("data", []):
                    comment["plataforma"] = "facebook"
                    comment["post_id"] = post["id"]
                    comments.append(comment)
            return comments
    except httpx.HTTPError as exc:
        logger.error("Error al obtener comentarios de Facebook: %s", exc)
        return []


async def get_instagram_comments(
    ig_access_token: str, ig_account_id: str, limit: int = 25
) -> list[dict]:
    """Obtiene comentarios recientes de Instagram Business."""
    try:
        async with httpx.AsyncClient() as client:
            # Obtener medios recientes
            media_resp = await client.get(
                f"{META_GRAPH_URL}/{ig_account_id}/media",
                params={
                    "fields": "id,caption,timestamp",
                    "limit": 10,
                    "access_token": ig_access_token,
                },
            )
            media_resp.raise_for_status()
            media_list = media_resp.json().get("data", [])

            comments: list[dict] = []
            for media in media_list[:5]:
                comm_resp = await client.get(
                    f"{META_GRAPH_URL}/{media['id']}/comments",
                    params={
                        "fields": "id,username,text,timestamp",
                        "limit": limit,
                        "access_token": ig_access_token,
                    },
                )
                comm_resp.raise_for_status()
                for comment in comm_resp.json().get("data", []):
                    comment["plataforma"] = "instagram"
                    comment["media_id"] = media["id"]
                    comments.append(comment)
            return comments
    except httpx.HTTPError as exc:
        logger.error("Error al obtener comentarios de Instagram: %s", exc)
        return []


async def get_messenger_messages(
    page_access_token: str, page_id: str, limit: int = 25
) -> list[dict]:
    """Obtiene mensajes recientes de Messenger para una página."""
    try:
        async with httpx.AsyncClient() as client:
            conv_resp = await client.get(
                f"{META_GRAPH_URL}/{page_id}/conversations",
                params={
                    "fields": "id,updated_time,messages.limit(10){id,message,created_time,from,to}",
                    "limit": limit,
                    "access_token": page_access_token,
                },
            )
            conv_resp.raise_for_status()
            conversations = conv_resp.json().get("data", [])

            messages: list[dict] = []
            for conversation in conversations:
                for msg in conversation.get("messages", {}).get("data", []):
                    msg["plataforma"] = "messenger"
                    msg["conversation_id"] = conversation.get("id")
                    messages.append(msg)
            return messages
    except httpx.HTTPError as exc:
        logger.error("Error al obtener DMs de Messenger: %s", exc)
        return []


async def get_instagram_direct_messages(
    ig_access_token: str, ig_account_id: str, limit: int = 25
) -> list[dict]:
    """Obtiene mensajes directos de Instagram (si la cuenta y permisos lo permiten)."""
    try:
        async with httpx.AsyncClient() as client:
            conv_resp = await client.get(
                f"{META_GRAPH_URL}/{ig_account_id}/conversations",
                params={
                    "fields": "id,updated_time,messages.limit(10){id,message,created_time,from}",
                    "limit": limit,
                    "access_token": ig_access_token,
                },
            )
            conv_resp.raise_for_status()
            conversations = conv_resp.json().get("data", [])

            messages: list[dict] = []
            for conversation in conversations:
                for msg in conversation.get("messages", {}).get("data", []):
                    msg["plataforma"] = "instagram_direct"
                    msg["conversation_id"] = conversation.get("id")
                    messages.append(msg)
            return messages
    except httpx.HTTPError as exc:
        logger.error("Error al obtener DMs de Instagram: %s", exc)
        return []


async def reply_to_comment(
    page_access_token: str, comment_id: str, message: str
) -> Optional[dict]:
    """Publica una respuesta a un comentario de Facebook/Instagram."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{META_GRAPH_URL}/{comment_id}/replies",
                data={"message": message, "access_token": page_access_token},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        logger.error("Error al responder comentario en Meta: %s", exc)
        return None


async def reply_to_direct_message(
    page_access_token: str, recipient_id: str, message: str
) -> Optional[dict]:
    """Envía un mensaje directo en Messenger usando el endpoint /me/messages."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{META_GRAPH_URL}/me/messages",
                json={
                    "recipient": {"id": recipient_id},
                    "messaging_type": "RESPONSE",
                    "message": {"text": message},
                    "access_token": page_access_token,
                },
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        logger.error("Error al responder DM en Meta: %s", exc)
        return None
