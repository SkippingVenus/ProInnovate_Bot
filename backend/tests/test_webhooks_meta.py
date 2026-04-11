"""Pruebas para webhook de Meta (BOT-6)."""

from app.models.business import Business
from app.models.message import Message


def test_meta_webhook_handshake(client, monkeypatch):
    monkeypatch.setattr("app.api.webhooks.settings.META_WEBHOOK_VERIFY_TOKEN", "verify-123")

    resp = client.get("/api/webhooks/meta", params={
        "hub.mode": "subscribe",
        "hub.verify_token": "verify-123",
        "hub.challenge": "777",
    })

    assert resp.status_code == 200
    assert resp.json() == 777


def test_meta_webhook_inserts_comment_message(client, db, monkeypatch):
    register = client.post("/api/auth/register", json={
        "email": "webhook@negocio.com",
        "password": "secreto123",
        "nombre": "Webhook Test",
        "rubro": "Restaurante",
    })
    assert register.status_code == 201

    business = db.query(Business).filter(Business.id == 1).first()
    business.fb_page_id = "page-123"
    business.system_prompt = ""
    db.commit()

    monkeypatch.setattr("app.api.webhooks.settings.META_APP_SECRET", "")

    payload = {
        "object": "page",
        "entry": [
            {
                "id": "page-123",
                "changes": [
                    {
                        "field": "feed",
                        "value": {
                            "comment_id": "comment-1",
                            "message": "Hola, quiero más información",
                            "from": {"id": "user-1", "name": "Cliente"},
                        },
                    }
                ],
            }
        ],
    }

    resp = client.post("/api/webhooks/meta", json=payload)
    assert resp.status_code == 200
    assert resp.json()["insertados"] == 1

    saved = db.query(Message).filter(Message.external_id == "comment-1").first()
    assert saved is not None
    assert saved.plataforma == "facebook"
    assert saved.tipo in ("comentario", "consulta", "queja", "elogio", "spam")
