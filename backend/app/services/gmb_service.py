"""Conector para Google My Business API."""
from __future__ import annotations

import logging
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

GMB_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GMB_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMB_API_BASE = "https://mybusinessaccountmanagement.googleapis.com/v1"
GMB_REVIEWS_BASE = "https://mybusiness.googleapis.com/v4"

GMB_SCOPES = [
    "https://www.googleapis.com/auth/business.manage",
]


def get_google_auth_url(state: str) -> str:
    """Genera la URL de autorización OAuth para Google My Business."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(GMB_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"{GMB_AUTH_URL}?{urlencode(params)}"


async def exchange_google_code(code: str) -> dict:
    """Intercambia el código de autorización por tokens de acceso de Google."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GMB_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "code": code,
                "grant_type": "authorization_code",
            },
        )
        response.raise_for_status()
        return response.json()


async def get_gmb_reviews(access_token: str, location_id: str, limit: int = 25) -> list[dict]:
    """Obtiene reseñas de Google My Business para una ubicación."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GMB_REVIEWS_BASE}/{location_id}/reviews",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"pageSize": limit},
            )
            response.raise_for_status()
            data = response.json()
            reviews = data.get("reviews", [])
            for review in reviews:
                review["plataforma"] = "google"
            return reviews
    except httpx.HTTPError as exc:
        logger.error("Error al obtener reseñas de Google My Business: %s", exc)
        return []


async def reply_to_review(
    access_token: str, location_id: str, review_id: str, reply_text: str
) -> Optional[dict]:
    """Publica una respuesta a una reseña de Google My Business."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{GMB_REVIEWS_BASE}/{location_id}/reviews/{review_id}/reply",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"comment": reply_text},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        logger.error("Error al responder reseña en Google My Business: %s", exc)
        return None


async def get_location_info(access_token: str, location_id: str) -> Optional[dict]:
    """Obtiene información de la ubicación en Google My Business."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GMB_API_BASE}/{location_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        logger.error("Error al obtener información de ubicación GMB: %s", exc)
        return None
