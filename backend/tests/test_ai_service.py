"""Pruebas del servicio de IA (sin llamadas reales a la API de Anthropic)."""
import pytest
from unittest.mock import patch, MagicMock

from app.services.ai_service import build_system_prompt, classify_and_respond


def test_build_system_prompt():
    """Verifica que el system prompt incluye los datos del negocio."""
    data = {
        "nombre": "Cevichería El Mar",
        "rubro": "Restaurante de mariscos",
        "tono": "cercano",
        "descripcion": "El mejor ceviche de Miraflores",
        "publico_objetivo": "Familias y turistas",
        "horario": "Lun-Dom 12pm-9pm",
        "whatsapp": "987654321",
    }
    prompt = build_system_prompt(data)
    assert "Cevichería El Mar" in prompt
    assert "Restaurante de mariscos" in prompt
    assert "987654321" in prompt
    assert "cercano" in prompt


def test_build_system_prompt_defaults():
    """Verifica que el system prompt maneja datos faltantes."""
    data = {"nombre": "Negocio Test", "rubro": "Servicios"}
    prompt = build_system_prompt(data)
    assert "Negocio Test" in prompt
    assert "Servicios" in prompt


def test_classify_and_respond_mock():
    """Verifica el clasificador con respuesta mockeada de Claude."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"tipo": "consulta", "urgencia": "baja", "respuesta_sugerida": "Gracias por escribirnos.", "razon_urgencia": ""}')]

    with patch("app.services.ai_service.anthropic.Anthropic") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.return_value = mock_response

        result = classify_and_respond("¿A qué hora abren?", "System prompt test")

    assert result["tipo"] == "consulta"
    assert result["urgencia"] == "baja"
    assert "respuesta_sugerida" in result
    assert result["urgente"] is False


def test_classify_high_urgency():
    """Verifica que las reseñas negativas se marcan como urgentes."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"tipo": "queja", "urgencia": "alta", "respuesta_sugerida": "Lamentamos mucho lo sucedido.", "razon_urgencia": "Reseña de 1 estrella"}')]

    with patch("app.services.ai_service.anthropic.Anthropic") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.return_value = mock_response

        result = classify_and_respond("[Reseña Google - 1 estrellas]: Pésimo servicio", "System prompt")

    assert result["urgente"] is True
    assert result["urgencia"] == "alta"
