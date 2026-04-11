"""Pruebas del endpoint de onboarding y perfil del negocio."""


def _register_and_get_token(client, email="biz@test.com"):
    resp = client.post("/api/auth/register", json={
        "email": email,
        "password": "clave123",
        "nombre": "Pollería Central",
        "rubro": "Restaurante",
    })
    return resp.json()["access_token"]


def test_onboarding(client):
    token = _register_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/businesses/onboarding", json={
        "nombre": "Cevichería El Puerto",
        "rubro": "Mariscos",
        "tono": "cercano",
        "descripcion": "Mariscos frescos del Callao",
        "publico_objetivo": "Familias limeñas",
        "horario": "Lun-Dom 11am-9pm",
        "whatsapp": "999888777",
    }, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["nombre"] == "Cevichería El Puerto"
    assert data["tono"] == "cercano"
    assert data["whatsapp"] == "999888777"


def test_onboarding_invalid_tono(client):
    token = _register_and_get_token(client, "inv@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/businesses/onboarding", json={
        "nombre": "Test",
        "rubro": "Test",
        "tono": "agresivo",  # Tono inválido
    }, headers=headers)
    assert resp.status_code == 400


def test_get_me(client):
    token = _register_and_get_token(client, "me@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/businesses/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@test.com"


def test_connection_status(client):
    token = _register_and_get_token(client, "conn@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/businesses/me/connections", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["facebook"] is False
    assert data["google"] is False
