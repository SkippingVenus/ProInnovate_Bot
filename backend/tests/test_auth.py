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
