# Documentación de la API de RepuBot

La documentación completa de la API está disponible en formato OpenAPI/Swagger:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Endpoints principales

### Autenticación (`/api/auth`)
- `POST /api/auth/register` — Registrar un nuevo negocio
- `POST /api/auth/login` — Iniciar sesión (JWT)
- `GET /api/auth/meta` — Iniciar flujo OAuth con Meta
- `GET /api/auth/meta/callback` — Callback OAuth de Meta
- `GET /api/auth/google` — Iniciar flujo OAuth con Google
- `GET /api/auth/google/callback` — Callback OAuth de Google

### Negocios (`/api/businesses`)
- `GET /api/businesses/me` — Perfil del negocio autenticado
- `POST /api/businesses/onboarding` — Completar el onboarding
- `PUT /api/businesses/me` — Actualizar datos del negocio
- `GET /api/businesses/me/connections` — Estado de conexiones OAuth

### Mensajes (`/api/messages`)
- `GET /api/messages/` — Listar mensajes (con filtros)
- `POST /api/messages/sync` — Sincronizar mensajes de todas las plataformas
- `POST /api/messages/{id}/approve` — Aprobar y publicar respuesta
- `POST /api/messages/{id}/ignore` — Ignorar un mensaje
- `POST /api/messages/{id}/regenerate` — Generar respuesta alternativa con IA

### Reportes (`/api/reports`)
- `GET /api/reports/dashboard` — Métricas del dashboard
- `GET /api/reports/metrics` — Historial de métricas por plataforma

### Competidores (`/api/competitors`)
- `GET /api/competitors/` — Listar competidores
- `POST /api/competitors/` — Agregar competidor
- `DELETE /api/competitors/{id}` — Eliminar competidor

### Webhooks (`/api/webhooks`)
- `POST /api/webhooks/culqi` — Webhook de pagos Culqi
- `POST /api/webhooks/meta` — Webhook de eventos Meta

## Autenticación

Todos los endpoints protegidos requieren un token JWT en el header:
```
Authorization: Bearer <token>
```

## Planes y precios

| Plan     | Precio  |
|----------|---------|
| Básico   | S/89    |
| Pro      | S/179   |
| Agencia  | S/399   |
