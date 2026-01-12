---
description: Configurar entorno local conectado a VPS
---

Este workflow configura tu entorno de desarrollo local para que se conecte a la base de datos del VPS.

## 1. Crear archivo .env.local

Crea el archivo `.env.local` en la raíz del proyecto con este contenido:

```env
# Base de Datos - Conecta al VPS vía SSH Tunnel
POSTGRES_USER=admin
POSTGRES_PASSWORD=secret
POSTGRES_DB=realestate_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

# Redis - Conecta al VPS vía SSH Tunnel  
REDIS_URL=redis://localhost:6380/0

# API Base URL para el frontend
VITE_API_BASE_URL=http://localhost:8000
```

## 2. Crear túneles SSH al VPS

Abre una terminal PowerShell y ejecuta:

```powershell
# Túnel para PostgreSQL (5432 del VPS → 5433 local)
ssh -L 5433:localhost:5432 vps-scraping -N -f

# Túnel para Redis (6379 del VPS → 6380 local)
ssh -L 6380:localhost:6379 vps-scraping -N -f
```

**Nota:** Los túneles quedan corriendo en segundo plano. Para cerrarlos:
```powershell
# Ver procesos SSH
Get-Process ssh

# Matar proceso específico
Stop-Process -Id <PID>
```

## 3. Modificar docker-compose para desarrollo local

Usa el archivo `docker-compose.local.yml` que se creará automáticamente.

## 4. Levantar servicios locales

```powershell
# Solo backend, worker y frontend (sin DB ni Redis locales)
docker-compose -f docker-compose.local.yml up -d
```

## 5. Verificar conexión

```powershell
# Verificar que el backend se conecta a la BD del VPS
docker-compose -f docker-compose.local.yml logs backend
```

Deberías ver logs indicando conexión exitosa a PostgreSQL.
