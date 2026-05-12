# 🎮 Guía de Uso - ProInnovate Bot

**Última actualización**: 12 de Mayo 2026  
**Versión**: 1.0

---

## 📋 Tabla de Contenidos

1. [Inicio Rápido](#inicio-rápido)
2. [Funcionalidades](#funcionalidades)
3. [Panel de Debug](#panel-de-debug)
4. [Sistema de Autenticación](#sistema-de-autenticación)
5. [Flujos Completos](#flujos-completos)
6. [Solución de Problemas](#solución-de-problemas)

---

## 🚀 Inicio Rápido

### Paso 1: Iniciar los Contenedores
```bash
cd ProInnovate_Bot
docker-compose up
```

Espera 30-40 segundos hasta ver:
```
✅ PostgreSQL: database system is ready
✅ Backend: Application startup complete
✅ Frontend: VITE ready
```

### Paso 2: Acceder a la Aplicación
```
http://localhost:5173
```

### Paso 3: Usar Demo Account (Rápido)
```
Email: demo@example.com
Password: demo123
```

Esto te lleva directamente al dashboard (onboarding ya completado).

---

## 🎯 Funcionalidades Principales

### 1. Registro de Usuario (Nuevo)

**Pantalla**: `/login` (Click "Crear cuenta")

**Pasos**:
```
1. Click "Crear cuenta"
2. Llenar formulario:
   - Email: tu@email.com
   - Contraseña: 8+ caracteres
   - Nombre: Tu nombre
   - Apellido: Tu apellido
3. Click "Crear cuenta"
```

**Resultado**:
- ✅ Cuenta creada (BD real o mock)
- ✅ Token JWT generado
- ✅ Redirige a onboarding

**¿Dónde se guarda?**:
- BD Real (PostgreSQL): Si servidor está corriendo ✅
- Mock (localStorage): Si servidor falla ✅
- Panel 🐛: Muestra dónde se guardó

---

### 2. Autenticación (Iniciar Sesión)

**Pantalla**: `/login`

**Pasos**:
```
1. Llenar email y contraseña
2. Click "Iniciar sesión"
```

**Resultado**:
- Si usuario ya completó onboarding → `/dashboard`
- Si usuario es nuevo → `/onboarding`

**Credenciales Demo**:
```
demo@example.com / demo123   (ya completó onboarding)
test@example.com / test123   (pendiente onboarding)
```

---

### 3. Onboarding (5 Secciones)

**Pantalla**: `/onboarding`

Formulario dividido en 5 pasos:

#### Paso 1: Información Básica
```
- Razón Social: Nombre del negocio
- RUC: Número de RUC
- País: Seleccionar país
- Ciudad: Seleccionar ciudad
- Dirección: Dirección del negocio
```

#### Paso 2: Datos de Contacto
```
- Teléfono: Número principal
- WhatsApp: Número para WhatsApp
- Email: Correo de contacto
```

#### Paso 3: Información de Negocios
```
- Tono: Cómo quieres que responda la IA
  (Profesional, Casual, Divertido, etc)
- Audiencia Objetivo: Descripción de clientes
- Plataforma Importante: FB, IG, Google, etc
```

#### Paso 4: Redes Sociales
```
- Seguidores Facebook: Número aproximado
- Seguidores Instagram: Número aproximado
- Frecuencia Publicación: Diaria, 3x/semana, etc
- Responde Comentarios: Sí o No
```

#### Paso 5: Desafíos
```
- Principal Desafío: Qué problema necesitas resolver
- Impacto en Ventas: Cómo esperas que ayude la IA
```

**Al Completar**:
- ✅ Datos guardados (BD real o mock)
- ✅ Negocio creado con perfil de IA
- ✅ Redirige a `/dashboard`

---

### 4. Dashboard (Área Principal)

**Pantalla**: `/dashboard`

**Vistas**:
- 📊 Métricas generales
- 📝 Mensajes por clasificar
- 🤝 Respuestas automáticas
- 📈 Reportes de IA
- ⚙️ Configuración

---

## 🐛 Panel de Debug

### Cómo Abrir

```
1. Abre http://localhost:5173
2. Mira esquina inferior derecha
3. Busca botón 🐛
4. Click para abrir/cerrar panel
```

### Qué Ves

**Estado General**:
```
Modo Mock: ✅ ACTIVO   (o ❌ Inactivo si usa BD real)
Token: jwt_asdfgh...   (primeros caracteres del JWT)
Usuario: demo@ex...    (usuario logueado actual)
```

**Estadísticas**:
```
Usuarios registrados: 5
Negocios creados: 3
```

**Lista de Usuarios**:
```
┌─────────────────────────────────────┐
│ demo@example.com                    │
│ ✅ Onboarding: Completo            │
│ [Login] [Editar]                    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ test@example.com                    │
│ ⏳ Onboarding: Pendiente            │
│ [Login] [Editar]                    │
└─────────────────────────────────────┘
```

**Lista de Negocios**:
```
┌─────────────────────────────────────┐
│ Mi Restaurante                      │
│ RUC: 20123456789 | Lima, PE        │
│ Tono: Profesional                   │
│ Plataforma: Instagram               │
└─────────────────────────────────────┘
```

### Acciones

**🔄 Refrescar**:
- Recarga datos del localStorage
- Útil si cambiaron datos en otra pestaña

**🗑️ Limpiar Todo**:
- **PELIGRO**: Borra TODOS los datos
- Cierra sesión
- Limpia localStorage
- Recarga página
- Vuelve a pantalla de login

**[Login]** (en cada usuario):
- Te loguea automáticamente como ese usuario
- Redirige al dashboard o onboarding según estado
- No requiere contraseña (solo en debug)

---

## 🔐 Sistema de Autenticación

### Flujo Normal (BD Real)

```
1. Usuario entra a /login
                ↓
2. Intenta conectar a BD
   (timeout: 3 segundos)
                ↓
3. ¿Responde BD?
   ├─ SÍ: Valida credenciales en PostgreSQL ✅
   └─ NO: Usa mock (localStorage) ✅
                ↓
4. Genera JWT token
                ↓
5. Guarda token en localStorage
                ↓
6. localStorage.setItem('token', 'jwt...')
                ↓
7. API interceptor inyecta token en headers
   Authorization: Bearer jwt...
                ↓
8. Redirige según estado:
   ├─ Nuevo usuario → /onboarding
   └─ Usuario existente → /dashboard
```

### Tokens JWT

**Formato**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwiZW1haWwiOiJkZW1vQGV4YW1wbGUuY29tIn0.signature
```

**Partes**:
```
[Header].[Payload].[Signature]
```

**Payload típico**:
```json
{
  "sub": "5",           // ID del usuario
  "email": "demo@...",
  "exp": 1234567890,    // Expiración
  "iat": 1234567800
}
```

**Dónde se almacena**:
```javascript
localStorage.getItem('token')  // Cliente
// En localStorage se ve como:
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Cómo se usa**:
```javascript
// En cada request API:
headers: {
  'Authorization': 'Bearer eyJhbGciOi...'
}
```

**Expiración**:
- Típicamente: 24 horas
- Si expira: Sistema redirige a /login
- Mostrar: "Tu sesión ha expirado"

---

## 📊 Flujos Completos

### Flujo 1: Registrarse y Completar Onboarding (Nuevo Usuario)

```
┌──────────────────────────┐
│ Abre http://localhost:5173
└────────────┬─────────────┘
             ↓
    ┌─────────────────────┐
    │ Pantalla de Login   │
    └────────┬────────────┘
             ↓
   ┌──────────────────────┐
   │ Click: Crear cuenta  │
   └────────┬─────────────┘
            ↓
  ┌────────────────────────┐
  │ Formulario Registro:   │
  │ - Email: nuevo@...     │
  │ - Password: pass123    │
  │ - Nombre: Tu nombre    │
  │ - Apellido: Tu apellido
  └────────┬───────────────┘
           ↓
  ┌─────────────────────────┐
  │ Click: Crear cuenta     │
  └────────┬────────────────┘
           ↓
  ┌──────────────────────────┐
  │ Sistema verifica:        │
  │ ¿BD disponible? (3seg)   │
  │ ├─ SÍ → Crea en BD      │
  │ └─ NO → Crea en mock    │
  └────────┬─────────────────┘
           ↓
  ┌──────────────────────┐
  │ Token generado ✅    │
  │ Guardado en          │
  │ localStorage         │
  └────────┬─────────────┘
           ↓
  ┌──────────────────────────┐
  │ Redirige a:              │
  │ /onboarding              │
  └────────┬─────────────────┘
           ↓
  ┌──────────────────────────┐
  │ Formulario Onboarding:   │
  │ Sección 1: Básica        │
  │ - Razón Social           │
  │ - RUC                    │
  │ - País, Ciudad, Dirección
  └────────┬─────────────────┘
           ↓
  ┌────────────────────┐
  │ Click: Siguiente   │
  └────────┬───────────┘
           ↓
  ┌─────────────────────────┐
  │ Secciones 2, 3, 4, 5    │
  │ (Mismo flujo)           │
  │ Rellenar, Siguiente     │
  └────────┬────────────────┘
           ↓
  ┌──────────────────────────┐
  │ Última sección:          │
  │ Click: Completar         │
  │ onboarding               │
  └────────┬─────────────────┘
           ↓
  ┌──────────────────────────┐
  │ Sistema valida y guarda: │
  │ ¿BD disponible?          │
  │ ├─ SÍ → Guarda en BD    │
  │ └─ NO → Guarda en mock  │
  └────────┬─────────────────┘
           ↓
  ┌──────────────────┐
  │ ✅ Completado!   │
  │ Redirige a:      │
  │ /dashboard       │
  └──────────────────┘
```

**Tiempo total**: ~5-10 minutos

---

### Flujo 2: Usar Demo Account (Rápido)

```
┌──────────────────────────┐
│ Abre http://localhost:5173
└────────────┬─────────────┘
             ↓
    ┌─────────────────────┐
    │ Pantalla de Login   │
    └────────┬────────────┘
             ↓
  ┌────────────────────────┐
  │ Llenar:                │
  │ Email: demo@example... │
  │ Pass: demo123          │
  └────────┬───────────────┘
           ↓
  ┌─────────────────────────┐
  │ Click: Iniciar sesión   │
  └────────┬────────────────┘
           ↓
  ┌──────────────────────────┐
  │ Sistema valida token     │
  │ en BD o mock (instant.)  │
  └────────┬─────────────────┘
           ↓
  ┌──────────────────────────┐
  │ Verifica si completó     │
  │ onboarding:              │
  │ demo@... → SÍ ✅        │
  └────────┬─────────────────┘
           ↓
  ┌────────────────────┐
  │ Redirige a:        │
  │ /dashboard ✅     │
  │ Ya listo para usar │
  └────────────────────┘
```

**Tiempo total**: ~5 segundos

---

### Flujo 3: Limpiar Datos y Empezar de 0

```
┌──────────────────────────┐
│ Abre http://localhost:5173
└────────────┬─────────────┘
             ↓
  ┌────────────────────────┐
  │ Mira esquina inferior   │
  │ derecha                 │
  └────────┬────────────────┘
           ↓
  ┌──────────────────────┐
  │ Busca botón 🐛      │
  │ Click para abrir     │
  │ panel debug          │
  └────────┬─────────────┘
           ↓
  ┌──────────────────────┐
  │ Panel se abre        │
  │ Mira botón:          │
  │ 🗑️ Limpiar Todo     │
  └────────┬─────────────┘
           ↓
  ┌──────────────────────┐
  │ Click "Limpiar Todo" │
  └────────┬─────────────┘
           ↓
  ┌──────────────────────────────┐
  │ Confirmación (opcional):     │
  │ "¿Borrar todo?"              │
  │ [Cancelar] [Sí, borrar]      │
  └────────┬─────────────────────┘
           ↓
  ┌──────────────────────────────┐
  │ Sistema borra:               │
  │ ✅ mock_users                │
  │ ✅ mock_businesses           │
  │ ✅ token                     │
  │ ✅ mockMode                  │
  └────────┬─────────────────────┘
           ↓
  ┌──────────────────────────────┐
  │ Página recarga               │
  │ localStorage = {}            │
  │ Vuelve a /login              │
  └────────┬─────────────────────┘
           ↓
  ┌────────────────────────┐
  │ ✅ Todo limpio!        │
  │ Listo para empezar 0   │
  └────────────────────────┘
```

**Tiempo total**: ~3 segundos

---

## 🆘 Solución de Problemas

### ❓ "Se queda en Cargando..."

**Síntoma**: Formulario muestra spinner infinito

**Causas posibles**:

1. **Backend no está corriendo**
   ```bash
   docker-compose ps
   # Debe mostrar 3 contenedores con estado "Up"
   ```
   
   **Solución**:
   ```bash
   docker-compose up
   # Espera 30 segundos
   ```

2. **Red de Docker no conecta correctamente**
   ```bash
   docker network ls
   docker network inspect proinnovate_bot_default
   ```
   
   **Solución**:
   ```bash
   docker-compose down
   docker system prune -a
   docker-compose up --build
   ```

3. **Puerto en uso**
   ```bash
   netstat -ano | find "5173"
   netstat -ano | find "8000"
   ```
   
   **Solución**:
   - Cambiar puerto en docker-compose.yml
   - O: Kill proceso usando puerto

---

### ❓ "Usuario ya registrado"

**Síntoma**: "Este email ya existe" aunque es cuenta nueva

**Causa**: Datos en localStorage o BD de sesión anterior

**Solución Opción A** (Rápida):
```javascript
// Abre F12 Developer Tools
// Tab: Console
localStorage.clear()
location.reload()
```

**Solución Opción B** (Visual):
1. Click 🐛
2. Click "🗑️ Limpiar Todo"
3. Recarga página

**Solución Opción C** (Usar otro email):
- Email 1: usuario1@test.com
- Email 2: usuario2@test.com
- Email 3: usuario3@test.com

---

### ❓ "¿Estoy usando BD real o mock?"

**Respuesta**: Abre panel de debug

```
1. Click 🐛 esquina inferior derecha
2. Mira: "Modo Mock: ✅ ACTIVO" o "❌ Inactivo"
   ├─ ✅ ACTIVO = Usando localStorage (mock)
   └─ ❌ Inactivo = Usando PostgreSQL (BD real)
```

---

### ❓ "Los datos se pierden al cerrar navegador"

**Síntoma**: Cierro navegador, vuelvo mañana, datos desaparecieron

**Causa**: localStorage es temporal (sesión solo)

**Explicación**:
```
localStorage PERSISTE = Mientras el navegador esté abierto
localStorage NO persiste = Cerrar navegador → datos se pierden

Si necesitas persistencia permanente:
→ Usar BD real (PostgreSQL)
```

**Nota**: Esto es normal y esperado en mock mode.

---

### ❓ "Error en console: 'Cannot read property token'"

**Síntoma**: 
```
TypeError: Cannot read property 'token' of undefined
```

**Causa**: Usuario no logueado

**Solución**:
```javascript
// En F12 Console:
localStorage.getItem('token')
// Si muestra: null
// Significa: No hay token, necesitas loguear

// Loguea usando:
// Email: demo@example.com
// Password: demo123
```

---

### ❓ "Veo muchos usuarios demo que no creé"

**Causa**: Usuarios precargados por defecto

**Lista de usuarios demo**:
```
demo@example.com / demo123       (precargado)
test@example.com / test123       (precargado)
nuevo@test.com / password123     (tu primer registro)
...
```

**Solución**: Click 🐛 → "🗑️ Limpiar Todo" para empezar limpio

---

### ❓ "Panel 🐛 no aparece"

**Causa**: Componente MockDebugger no está importado

**Verificar**:
```javascript
// Abre: frontend/src/App.jsx
// Debe contener:

import MockDebugger from './utils/mockDebugger.jsx'

function App() {
  return (
    <>
      {/* ... */}
      <MockDebugger />  {/* ← Este debe estar aquí */}
    </>
  )
}
```

**Solución**:
```bash
# Si no está, agrégalo
# Luego: docker-compose restart frontend
```

---

### ❓ "Quiero probar con BD desconectada"

**Pasos**:
```bash
1. docker-compose up  # Inicia todo
2. Dejar corriendo
3. docker-compose pause backend  # Pausa backend (no mata)
   O
   docker stop proinnovate_bot-backend-1
4. Intentar registrarse
5. ✅ Sistema usa mock automáticamente
6. 🐛 Panel muestra "Modo Mock: ✅ ACTIVO"
7. docker-compose unpause backend  # Reactivar
   O
   docker start proinnovate_bot-backend-1
```

---

## 📞 Contacto y Soporte

**Problemas comunes**: Ver sección anterior

**Logs para debugging**:
```bash
# Frontend logs
docker-compose logs -f frontend

# Backend logs
docker-compose logs -f backend

# Todos los logs
docker-compose logs -f
```

**Reset total** (última opción):
```bash
docker-compose down -v        # Remove volumes
docker system prune -a        # Clean everything
docker-compose up --build     # Rebuild fresh
```

---

## ✅ Checklist de Uso

- [ ] Contenedores corriendo (`docker-compose ps`)
- [ ] Frontend accesible (http://localhost:5173)
- [ ] Panel 🐛 visible
- [ ] Prueba con demo account (rápido)
- [ ] Prueba registro nuevo
- [ ] Prueba onboarding completo
- [ ] Prueba panel debug
- [ ] Prueba limpiar datos
- [ ] Prueba con BD desconectada (opcional)

---

**Generado**: 12 de Mayo 2026  
**Status**: ✅ Guía completa  
**Versión**: 1.0

*¿Necesitas algo más? Revisa CAMBIOS_IMPLEMENTADOS.md para detalles técnicos.*
