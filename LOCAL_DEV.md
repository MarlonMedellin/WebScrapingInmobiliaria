# Desarrollo Local Conectado a VPS

Esta configuración te permite desarrollar localmente mientras usas la base de datos de producción del VPS.

## 🎯 Arquitectura

```
Local (Tu PC)                    VPS (Producción)
├─ Frontend (React)              
├─ Backend (FastAPI)             
├─ Worker (Celery)               
│                                
└─ SSH Tunnels ──────────────→  ├─ PostgreSQL
                                 └─ Redis
```

## 🚀 Inicio Rápido

### Opción 1: Script Automatizado (Recomendado)

```powershell
.\start-local-dev.ps1
```

Este script:
1. ✅ Crea túneles SSH automáticamente
2. ✅ Genera el archivo `.env.local` si no existe
3. ✅ Levanta los servicios Docker
4. ✅ Verifica el estado

### Opción 2: Manual

#### 1. Crear túneles SSH

```powershell
# PostgreSQL
ssh -L 5433:localhost:5432 vps-scraping -N -f

# Redis
ssh -L 6380:localhost:6379 vps-scraping -N -f
```

#### 2. Crear archivo `.env.local`

```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=secret
POSTGRES_DB=realestate_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

REDIS_URL=redis://localhost:6380/0

VITE_API_BASE_URL=http://localhost:8000
```

#### 3. Levantar servicios

```powershell
docker compose -f docker-compose.local.yml up -d
```

## 📋 Comandos Útiles

### Ver logs en tiempo real
```powershell
docker compose -f docker-compose.local.yml logs -f
```

### Ver logs de un servicio específico
```powershell
docker compose -f docker-compose.local.yml logs -f backend
docker compose -f docker-compose.local.yml logs -f worker
docker compose -f docker-compose.local.yml logs -f frontend
```

### Reiniciar un servicio
```powershell
docker compose -f docker-compose.local.yml restart backend
```

### Detener todo
```powershell
docker compose -f docker-compose.local.yml down
```

### Cerrar túneles SSH
```powershell
# Ver procesos SSH
Get-Process ssh

# Cerrar todos los túneles SSH
Get-Process ssh | Stop-Process
```

## 🔍 Verificación

### 1. Verificar túneles SSH activos
```powershell
Get-Process ssh | Format-Table Id, ProcessName, StartTime
```

### 2. Verificar conexión a PostgreSQL del VPS
```powershell
# Desde tu máquina local
Test-NetConnection localhost -Port 5433
```

### 3. Verificar que el backend se conecta correctamente
```powershell
docker compose -f docker-compose.local.yml logs backend | Select-String "database"
```

Deberías ver algo como: `INFO: Connected to database`

### 4. Probar consulta a la BD
```powershell
# Conectar a PostgreSQL del VPS vía túnel
docker run --rm -it --network host postgres:16-alpine psql -h localhost -p 5433 -U admin -d realestate_db

# Dentro de psql:
SELECT COUNT(*) FROM properties;
```

## 🛠️ Troubleshooting

### Error: "Connection refused" en PostgreSQL

**Causa:** El túnel SSH no está activo.

**Solución:**
```powershell
# Verificar túneles
Get-Process ssh

# Si no hay ninguno, crear de nuevo
ssh -L 5433:localhost:5432 vps-scraping -N -f
ssh -L 6380:localhost:6379 vps-scraping -N -f
```

### Error: "Port already in use"

**Causa:** Ya hay un servicio usando el puerto 5433 o 6380.

**Solución:**
```powershell
# Ver qué proceso usa el puerto
Get-NetTCPConnection -LocalPort 5433

# Cambiar el puerto en .env.local y docker-compose.local.yml
```

### Los scrapers no guardan datos

**Causa:** El worker no se conecta correctamente a la BD.

**Solución:**
```powershell
# Ver logs del worker
docker compose -f docker-compose.local.yml logs worker

# Reiniciar el worker
docker compose -f docker-compose.local.yml restart worker
```

### El frontend muestra "localhost:8000/searches" error

**Causa:** El archivo `config.js` no se está importando correctamente.

**Solución:**
```powershell
# Reconstruir el frontend
docker compose -f docker-compose.local.yml up -d --build frontend
```

## 📊 Diferencias con Producción

| Aspecto | Local | VPS (Producción) |
|---------|-------|------------------|
| **Base de Datos** | VPS (vía túnel) | VPS (directo) |
| **Redis** | VPS (vía túnel) | VPS (directo) |
| **Backend** | Local (puerto 8000) | VPS (puerto 8000) |
| **Frontend** | Local (puerto 5173) | VPS (puerto 80 vía Nginx) |
| **Scrapers** | Local → Guardan en VPS | VPS → Guardan en VPS |

## ⚠️ Consideraciones Importantes

1. **Datos compartidos:** Los scrapers locales guardarán en la misma BD que producción
2. **Testing:** Usa filtros o marca las propiedades de testing para diferenciarlas
3. **Performance:** El túnel SSH puede ser más lento que una conexión directa
4. **Seguridad:** No commitees el archivo `.env.local` (ya está en `.gitignore`)

## 🔄 Workflow de Desarrollo

1. **Hacer cambios** en el código local
2. **Probar localmente** con datos reales del VPS
3. **Commit y push** a GitHub
4. **Deploy en VPS:**
   ```bash
   ssh vps-scraping
   cd /root/WebScrapingInmobiliaria
   git pull origin main
   docker compose restart worker backend
   ```

## 📚 Recursos

- [Workflow completo](.agent/workflows/setup-local-dev.md)
- [Docker Compose local](docker-compose.local.yml)
- [Script de inicio](start-local-dev.ps1)
