# 🤖 ProInnovate Bot - Sistema de Gestión Inteligente

**Status**: ✅ Operativo  
**Última actualización**: 12 de Mayo 2026  
**Versión**: 1.0

Agente de marketing digital con IA para pequeños negocios. Lee, clasifica y responde comentarios, DMs y reseñas en Facebook, Instagram y Google Maps.

---

## 🚀 Inicio Rápido

### Requisitos
- Docker Desktop instalado
- Puertos disponibles: 5173, 8000, 5432

### Pasos

```bash
cd ProInnovate_Bot
docker-compose up
# Accede a http://localhost:5173
```

**Demo Account**:
- Email: `demo@example.com`
- Password: `demo123`

---

## 🏗️ Stack Tecnológico

| Capa | Tecnología |
|-----|-----------|
| **Frontend** | React 19 + Vite + Tailwind CSS |
| **Backend** | FastAPI + Python |
| **BD** | PostgreSQL 16 + SQLAlchemy + Alembic |
| **IA** | Anthropic Claude |
| **Autenticación** | JWT + OAuth2 (Meta, Google) |
| **Pago** | Culqi (peruana) |

---

## 📁 Estructura

```
ProInnovate_Bot/
├── backend/
│   ├── app/
│   │   ├── api/        # Rutas (auth, businesses, messages, etc)
│   │   ├── models/     # ORM Models
│   │   ├── services/   # Lógica de negocio
│   │   └── core/       # Configuración y seguridad
│   └── tests/          # Tests unitarios
├── frontend/
│   ├── src/
│   │   ├── pages/      # Login, Onboarding, Dashboard, etc
│   │   ├── components/ # UI reutilizable
│   │   ├── utils/
│   │   │   ├── mockAuth.js       # ✨ Mock authentication
│   │   │   └── mockDebugger.jsx  # ✨ Debug panel
│   │   └── api/
│   └── vite.config.js  # Proxy configurado
└── docker-compose.yml
```

---

## ✨ Cambios Recientes (Mayo 2026)

### 🔌 Proxy Network Corregido
- **Problema**: Frontend no alcanzaba backend API (`ECONNREFUSED`)
- **Causa**: vite.config.js usaba `localhost:8000` (incorrecto en Docker)
- **Solución**: Cambiar a `http://backend-1:8000` (nombre del servicio)
- **Resultado**: ✅ Conectividad completamente funcional

### 🎯 Sistema Mock Auth Implementado
**Archivos nuevos**:
- `frontend/src/utils/mockAuth.js` - Registro y login sin BD
- `frontend/src/utils/mockDebugger.jsx` - Panel flotante 🐛

**Archivos modificados**:
- `Login.jsx` - Fallback a mock si BD falla
- `OnboardingFlow.jsx` - Guardar en mock si BD falla
- `App.jsx` - Agregado panel debug
- `client.js` - Timeout: 3000ms
- `vite.config.js` - Proxy corregido

**Features**:
- ✅ Funciona sin base de datos
- ✅ Activación automática si BD falla
- ✅ Datos en localStorage (persistentes en sesión)
- ✅ Panel debug flotante 🐛
- ✅ Usuarios demo precargados
- ✅ Sistema híbrido: BD real + fallback mock

---

## 🧪 Guía de Uso Rápida

### 1. Panel de Debug 🐛
```
Click esquina inferior derecha → Ver todos los datos
├── Usuarios registrados
├── Negocios creados
├── Token actual
├── Quick-login buttons
└── Reset de datos
```

### 2. Test sin BD
```
1. docker-compose down (detener backend)
2. Intentar registrarse
3. ✅ Sistema usa mock automáticamente
4. 🐛 Panel muestra "Modo Mock: ✅ ACTIVO"
```

### 3. Limpiar datos
```
Opción A: Click 🐛 → "🗑️ Limpiar Todo"
Opción B: F12 → Application → localStorage → Delete All
```

---

## 🔐 Usuarios Demo

| Email | Contraseña | Estado |
|-------|-----------|--------|
| demo@example.com | demo123 | Onboarding completo |
| test@example.com | test123 | Onboarding pendiente |

---

## 📊 localStorage Keys

```javascript
mock_users        // Usuarios registrados
mock_businesses   // Negocios/onboarding
token             // JWT actual
mockMode          // ¿Mock activado?
```

---

## 🔄 Flujo de Autenticación

```
Usuario → http://localhost:5173
    ↓
1. Intenta conectar a BD real (timeout: 3seg)
    ↓
2. ¿Responde?
    ├─ SÍ → Usa BD (PostgreSQL) ✅
    └─ NO → Usa Mock (localStorage) ✅
    ↓
3. Genera JWT token
    ↓
4. Guarda datos (BD o mock)
    ↓
5. Redirige a Onboarding (usuario nuevo)
       o Dashboard (usuario existente)
```

---

## 📞 Troubleshooting

| Problema | Solución |
|----------|----------|
| "Se queda cargando" | Abre F12 Console, busca errores rojos |
| "Conexión rechazada" | Verifica: `docker-compose ps` |
| "Usuario ya registrado" | Click 🐛 → "Limpiar Todo" |
| "¿Uso BD o mock?" | Click 🐛 → Mira estado |
| "Puertos en uso" | `netstat -an \| find "5173"` |

---

## ✅ Checklist de Setup

- [x] Backend corriendo (FastAPI healthy)
- [x] Frontend corriendo (Vite ready)
- [x] PostgreSQL conectada
- [x] Proxy Docker configurado
- [x] Mock auth funcional
- [x] Panel debug operativo
- [x] Usuarios demo precargados
- [x] Sin errores de compilación

---

## 📚 Documentación Adicional

- **CAMBIOS_IMPLEMENTADOS.md** - Detalles técnicos de cambios
- **COMO_USAR.md** - Guía completa de funcionalidades

---

**Status**: ✅ Listo para desarrollo y testing  
**Versión**: 1.0 | Mayo 2026

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

