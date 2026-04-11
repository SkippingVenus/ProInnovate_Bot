# RepuBot 🤖

**Agente de marketing digital con IA para pequeños negocios en Lima, Perú**

RepuBot actúa como community manager automatizado: lee, clasifica y responde comentarios, DMs y reseñas en Facebook, Instagram y Google Maps, usando IA (Anthropic Claude) para adaptarse al tono de cada negocio.

## Stack tecnológico

- **Frontend**: React + Tailwind CSS (Vite, SPA)
- **Backend**: Python + FastAPI
- **Base de datos**: PostgreSQL + SQLAlchemy + Alembic
- **IA**: Anthropic Claude (`claude-sonnet-4-6`)
- **Autenticación**: JWT + OAuth2 para Meta Graph API y Google APIs
- **Pagos**: Culqi (pasarela de pago peruana)

## Estructura del proyecto

```
.
├── backend/            # FastAPI + Python
│   ├── app/
│   │   ├── api/        # Rutas (auth, messages, businesses, webhooks, reports, competitors)
│   │   ├── core/       # Config, JWT, seguridad, cifrado, base de datos
│   │   ├── models/     # SQLAlchemy: Business, Message, Competitor, Metric, Subscription
│   │   └── services/   # Claude AI, Meta, Google My Business, Culqi
│   ├── alembic/        # Migraciones de base de datos
│   └── tests/          # Pruebas unitarias
├── frontend/           # React + Vite + Tailwind
│   └── src/
│       ├── api/        # Cliente axios + custom hooks
│       ├── components/ # MessageCard, MetricWidget, AlertBanner, Sidebar
│       └── pages/      # Dashboard, Inbox, Competitors, Reports, Settings, Login
├── docs/               # Documentación de la API
├── docker-compose.yml  # Postgres + Backend + Frontend
└── .env.example        # Variables de entorno requeridas
```

## Inicio rápido

### Con Docker Compose

```bash
cp .env.example .env
# Edita .env con tus claves de API
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### Desarrollo local

**Backend:**
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Planes

| Plan     | Precio  | Incluye                     |
|----------|---------|-----------------------------|
| Básico   | S/89/mes| FB + IG, modo supervisado   |
| Pro      | S/179/mes| FB + IG + Google, automático|
| Agencia  | S/399/mes| 5 negocios, soporte 24/7   |

## Variables de entorno requeridas

Ver `.env.example` para la lista completa de variables necesarias.

