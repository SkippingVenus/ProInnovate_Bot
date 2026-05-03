"""Tests para el endpoint de verificación de webhooks de Meta."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.core.config import get_settings

client = TestClient(app)


@patch("app.api.webhooks.settings")
def test_meta_webhook_verify_success(mock_settings):
    """Verifica que el endpoint retorna 200 + challenge cuando los parámetros son válidos."""
    mock_settings.META_WEBHOOK_VERIFY_TOKEN = "test-verify-token"
    
    response = client.get(
        "/api/webhooks/meta",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test-verify-token",
            "hub.challenge": "1234567890",
        }
    )
    
    assert response.status_code == 200
    assert response.text == "1234567890"
    assert response.headers["content-type"] == "text/plain; charset=utf-8"


@patch("app.api.webhooks.settings")
def test_meta_webhook_verify_invalid_token(mock_settings):
    """Verifica que retorna 403 si el token no coincide."""
    mock_settings.META_WEBHOOK_VERIFY_TOKEN = "correct-token"
    
    response = client.get(
        "/api/webhooks/meta",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "1234567890",
        }
    )
    
    assert response.status_code == 403


@patch("app.api.webhooks.settings")
def test_meta_webhook_verify_invalid_mode(mock_settings):
    """Verifica que retorna 400 si hub.mode no es 'subscribe'."""
    mock_settings.META_WEBHOOK_VERIFY_TOKEN = "test-verify-token"
    
    response = client.get(
        "/api/webhooks/meta",
        params={
            "hub.mode": "unsubscribe",
            "hub.verify_token": "test-verify-token",
            "hub.challenge": "1234567890",
        }
    )
    
    assert response.status_code == 400


@patch("app.api.webhooks.settings")
def test_meta_webhook_verify_missing_challenge(mock_settings):
    """Verifica que retorna 400 si falta hub.challenge."""
    mock_settings.META_WEBHOOK_VERIFY_TOKEN = "test-verify-token"
    
    response = client.get(
        "/api/webhooks/meta",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test-verify-token",
        }
    )
    
    assert response.status_code == 400


@patch("app.api.webhooks.settings")
def test_meta_webhook_verify_no_params(mock_settings):
    """Verifica que retorna 400 si no hay parámetros."""
    response = client.get("/api/webhooks/meta")
    
    assert response.status_code == 400
