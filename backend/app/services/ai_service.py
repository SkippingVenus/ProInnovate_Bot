"""Servicio de IA usando Anthropic Claude para clasificar y responder mensajes."""
from __future__ import annotations

import json
import logging
from typing import Optional

import anthropic

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Plantilla base del system prompt del agente
SYSTEM_PROMPT_TEMPLATE = """Eres el community manager digital de {nombre}, un negocio de {rubro} ubicado en Lima, Perú.

Perfil del negocio:
- Descripción: {descripcion}
- Público objetivo: {publico_objetivo}
- Horario de atención: {horario}
- WhatsApp para pedidos: {whatsapp}
- Tono de comunicación: {tono}

Instrucciones de comportamiento:
1. Responde siempre en español peruano, de manera {tono_instruccion}.
2. Para comentarios en redes sociales: máximo 3 líneas.
3. Siempre ofrece valor al cliente: resuelve dudas, agradece elogios, atiende quejas con empatía.
4. Si el cliente tiene una queja grave, pide disculpas y ofrece solución concreta.
5. Para pedidos, invita a escribir al WhatsApp: {whatsapp}.
6. Nunca hagas promesas que el negocio no pueda cumplir.
7. Reprime el spam de forma breve y educada.

Contexto cultural: Los clientes son limeños. Usa expresiones peruanas cuando el tono sea cercano o divertido."""

TONO_MAP = {
    "cercano": "amigable y cercana, como si fuera un amigo de confianza",
    "profesional": "profesional y formal, manteniendo siempre la cortesía",
    "divertido": "divertida y con humor, usando expresiones peruanas frescas",
}


def build_system_prompt(business_data: dict) -> str:
    """Genera el system prompt personalizado para un negocio."""
    tono = business_data.get("tono", "profesional")
    return SYSTEM_PROMPT_TEMPLATE.format(
        nombre=business_data.get("nombre", ""),
        rubro=business_data.get("rubro", ""),
        descripcion=business_data.get("descripcion", "Sin descripción disponible"),
        publico_objetivo=business_data.get("publico_objetivo", "Público general"),
        horario=business_data.get("horario", "Consultar"),
        whatsapp=business_data.get("whatsapp", "No disponible"),
        tono=tono,
        tono_instruccion=TONO_MAP.get(tono, TONO_MAP["profesional"]),
    )


def classify_and_respond(
    message_content: str,
    system_prompt: str,
    platform: str = "general",
) -> dict:
    """
    Clasifica un mensaje y genera una respuesta sugerida usando Claude.

    Retorna un dict con:
    - tipo: consulta | queja | elogio | spam
    - urgencia: alta | media | baja
    - respuesta_sugerida: texto de respuesta
    - urgente: bool (True si requiere alerta al dueño)
    """
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    classification_prompt = f"""Analiza el siguiente mensaje de {platform} y devuelve un JSON con este formato exacto:
{{
  "tipo": "consulta|queja|elogio|spam",
  "urgencia": "alta|media|baja",
  "respuesta_sugerida": "texto de respuesta (máximo 3 líneas para comentarios)",
  "razon_urgencia": "breve explicación si urgencia es alta"
}}

Criterios de urgencia alta:
- Reseña de 1 o 2 estrellas
- Queja pública con palabras fuertes
- Mención de problema de salud, seguridad o devolución de dinero

Mensaje a analizar:
{message_content}

Responde SOLO con el JSON, sin explicaciones adicionales."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": classification_prompt}],
        )
        raw = response.content[0].text.strip()
        # Limpiar posibles bloques de código markdown
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        result["urgente"] = result.get("urgencia") == "alta"
        return result
    except (json.JSONDecodeError, anthropic.APIError) as exc:
        logger.error("Error al clasificar mensaje con Claude: %s", exc)
        return {
            "tipo": "consulta",
            "urgencia": "media",
            "respuesta_sugerida": "Gracias por tu mensaje. Pronto nos pondremos en contacto contigo.",
            "urgente": False,
        }


def generate_alternative_response(
    message_content: str,
    system_prompt: str,
    previous_response: Optional[str] = None,
) -> str:
    """Genera una respuesta alternativa (cuando el usuario pide otra versión)."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    context = ""
    if previous_response:
        context = f"\n\nLa respuesta anterior fue:\n{previous_response}\n\nGenera una versión diferente, con otro enfoque."

    prompt = f"""Genera una respuesta alternativa para este mensaje de cliente:{context}

Mensaje:
{message_content}

Responde SOLO con el texto de la respuesta, sin comillas ni explicaciones. Máximo 3 líneas."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except anthropic.APIError as exc:
        logger.error("Error al generar respuesta alternativa con Claude: %s", exc)
        return "Gracias por tu mensaje. En breve te atendemos."
