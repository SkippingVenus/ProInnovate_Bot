from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.core.config import get_settings
from app.api import auth, businesses, messages, reports, webhooks, competitors

settings = get_settings()

app = FastAPI(
    title="MarkiBot API",
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
    return {"service": "MarkiBot API", "status": "ok", "version": "1.0.0"}

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

# ==================== Endpoints legales para Meta ====================

@app.get("/privacy", response_class=HTMLResponse, tags=["legal"])
async def privacy_policy():
    """Política de privacidad requerida por Meta"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Política de Privacidad - MarkiBot</title>
        <style>
            body { font-family: -apple-system, sans-serif; max-width: 800px; 
                   margin: 50px auto; padding: 20px; line-height: 1.6; }
            h1 { color: #1877f2; }
            h2 { color: #333; margin-top: 30px; }
        </style>
    </head>
    <body>
        <h1>Política de Privacidad</h1>
        <p><strong>Última actualización:</strong> Abril 2026</p>
        
        <h2>1. Información que recopilamos</h2>
        <p>MarkiBot recopila:</p>
        <ul>
            <li>Nombre de tu negocio y página</li>
            <li>Comentarios y mensajes de Facebook e Instagram</li>
            <li>Reseñas de Google My Business</li>
            <li>Métricas de engagement</li>
        </ul>
        
        <h2>2. Uso de información</h2>
        <p>Usamos tu información para:</p>
        <ul>
            <li>Generar respuestas automáticas con IA</li>
            <li>Analizar rendimiento de publicaciones</li>
            <li>Crear reportes de métricas</li>
        </ul>
        
        <h2>3. Compartir información</h2>
        <p>NO compartimos ni vendemos tu información a terceros.</p>
        
        <h2>4. Seguridad</h2>
        <p>Tokens de acceso encriptados con cifrado Fernet.</p>
        
        <h2>5. Contacto</h2>
        <p>Email: contacto@markibot.com</p>
    </body>
    </html>
    """

@app.get("/terms", response_class=HTMLResponse, tags=["legal"])
async def terms_of_service():
    """Términos de servicio requeridos por Meta"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Términos de Servicio - MarkiBot</title>
        <style>
            body { font-family: -apple-system, sans-serif; max-width: 800px; 
                   margin: 50px auto; padding: 20px; line-height: 1.6; }
            h1 { color: #1877f2; }
            h2 { color: #333; margin-top: 30px; }
        </style>
    </head>
    <body>
        <h1>Términos de Servicio</h1>
        <p><strong>Última actualización:</strong> Abril 2026</p>
        
        <h2>1. Descripción</h2>
        <p>MarkiBot es un agente de marketing digital con IA para pequeños negocios.</p>
        
        <h2>2. Uso del servicio</h2>
        <p>Aceptas que:</p>
        <ul>
            <li>Eres propietario o administrador de las cuentas conectadas</li>
            <li>Revisarás respuestas generadas antes de aprobarlas</li>
            <li>No usarás el servicio para spam o actividades ilícitas</li>
        </ul>
        
        <h2>3. Responsabilidades</h2>
        <p>Eres responsable del contenido final publicado en tus redes.</p>
        
        <h2>4. Contacto</h2>
        <p>Email: contacto@markibot.com</p>
    </body>
    </html>
    """

@app.get("/data-deletion", response_class=HTMLResponse, tags=["legal"])
async def data_deletion():
    """Instrucciones de eliminación de datos para Meta"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Eliminación de Datos - MarkiBot</title>
        <style>
            body { font-family: -apple-system, sans-serif; max-width: 800px; 
                   margin: 50px auto; padding: 20px; line-height: 1.6; }
            h1 { color: #1877f2; }
            h2 { color: #333; margin-top: 30px; }
        </style>
    </head>
    <body>
        <h1>Eliminación de Datos</h1>
        
        <h2>Cómo eliminar tus datos</h2>
        <p><strong>Opción 1:</strong> Desde el panel → Configuración → Eliminar cuenta</p>
        <p><strong>Opción 2:</strong> Email a contacto@markibot.com con:</p>
        <ul>
            <li>Tu correo registrado</li>
            <li>Nombre de tu negocio</li>
        </ul>
        
        <h2>Qué se elimina</h2>
        <ul>
            <li>Información del negocio</li>
            <li>Historial de mensajes</li>
            <li>Tokens de acceso encriptados</li>
            <li>Métricas y reportes</li>
        </ul>
        
        <h2>Tiempo</h2>
        <p>Máximo 30 días. Esta acción es irreversible.</p>
    </body>
    </html>
    """