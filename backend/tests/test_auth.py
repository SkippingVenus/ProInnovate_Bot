"""Pruebas de la API de autenticación."""
import pytest


def test_register_and_login(client):
    # Registro
    resp = client.post("/api/auth/register", json={
        "email": "test@negocio.com",
        "password": "secreto123",
        "nombre": "Pollería Los Andes",
        "rubro": "Restaurante",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Login con credenciales correctas
    resp = client.post("/api/auth/login", data={
        "username": "test@negocio.com",
        "password": "secreto123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_register_duplicate_email(client):
    payload = {
        "email": "dup@negocio.com",
        "password": "clave123",
        "nombre": "Tienda ABC",
        "rubro": "Retail",
    }
    client.post("/api/auth/register", json=payload)
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 400


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "email": "wrong@test.com",
        "password": "correcto",
        "nombre": "Test",
        "rubro": "Test",
    })
    resp = client.post("/api/auth/login", data={
        "username": "wrong@test.com",
        "password": "incorrecto",
    })
    assert resp.status_code == 401


def test_get_business_without_token(client):
    resp = client.get("/api/businesses/me")
    assert resp.status_code == 401


def test_meta_connect_returns_oauth_url(client):
    client.post("/api/auth/register", json={
        "email": "meta@negocio.com",
        "password": "secreto123",
        "nombre": "Meta Test",
        "rubro": "Retail",
    })

    resp = client.get("/api/auth/meta/connect", params={"negocio_id": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert "url" in data
    assert "facebook.com" in data["url"]


def test_meta_callback_and_disconnect_flow(client, monkeypatch):
    register = client.post("/api/auth/register", json={
        "email": "callback@negocio.com",
        "password": "secreto123",
        "nombre": "Callback Test",
        "rubro": "Servicios",
    })
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    async def fake_exchange_meta_code(code: str):
        return {"access_token": "user-token"}

    async def fake_get_primary_page_connection(user_access_token: str):
        return {
            "fb_page_id": "123456789",
            "fb_page_name": "Mi Pagina",
            "fb_access_token": "page-token",
            "ig_account_id": "ig-123",
        }

    monkeypatch.setattr("app.api.auth.exchange_meta_code", fake_exchange_meta_code)
    monkeypatch.setattr("app.api.auth.get_primary_page_connection", fake_get_primary_page_connection)

    callback = client.get("/api/auth/meta/callback", params={"code": "ok", "state": "1"})
    assert callback.status_code == 200
    callback_data = callback.json()
    assert callback_data["fb_page_id"] == "123456789"
    assert callback_data["ig_account_id"] == "ig-123"

    profile = client.get("/api/businesses/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["fb_page_id"] == "123456789"
    assert profile.json()["fb_page_name"] == "Mi Pagina"

    disconnect = client.delete("/api/auth/meta/disconnect/1", headers=headers)
    assert disconnect.status_code == 200

    profile_after = client.get("/api/businesses/me", headers=headers)
    assert profile_after.status_code == 200
    assert profile_after.json()["fb_page_id"] is None
    assert profile_after.json()["ig_account_id"] is None
