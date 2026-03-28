from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api import auth, businesses, messages, reports, webhooks, competitors

settings = get_settings()

app = FastAPI(
    title="RepuBot API",
    description="Agente de marketing digital con IA para pequeños negocios en Lima, Perú",
    version="1.0.0",
)

# CORS para el frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(auth.router)
app.include_router(businesses.router)
app.include_router(messages.router)
app.include_router(reports.router)
app.include_router(webhooks.router)
app.include_router(competitors.router)


@app.get("/", tags=["health"])
def root():
    return {"service": "RepuBot API", "status": "ok", "version": "1.0.0"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
