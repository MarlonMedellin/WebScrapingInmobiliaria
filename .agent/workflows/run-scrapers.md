---
description: ejecutar scrapers directamente sin docker
---

# Ejecutar Scrapers Localmente (Sin Docker)

Este workflow te permite ejecutar los scrapers de Celery directamente en tu máquina local, conectándose a la base de datos del VPS.

## Prerequisitos

1. Túneles SSH activos al VPS
2. Python 3.12 instalado
3. Entorno virtual configurado

## Pasos

### 1. Verificar túneles SSH activos

```powershell
Get-Process ssh | Format-Table Id, ProcessName, StartTime
```

Si no hay túneles activos, créalos:

```powershell
ssh -L 5433:localhost:5432 vps-scraping -N -f
ssh -L 6380:localhost:6379 vps-scraping -N -f
```

### 2. Navegar al directorio backend

```powershell
cd backend
```

### 3. Crear y activar entorno virtual (solo primera vez)

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1
```

### 4. Instalar dependencias (solo primera vez)

```powershell
pip install -r requirements.txt
playwright install chromium
```

### 5. Configurar variables de entorno

```powershell
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5433"
$env:POSTGRES_USER="admin"
$env:POSTGRES_PASSWORD="secret"
$env:POSTGRES_DB="realestate_db"
$env:REDIS_URL="redis://localhost:6380/0"
```

### 6. Ejecutar Celery worker

```powershell
celery -A core.worker.celery_app worker --loglevel=info --concurrency=3
```

El worker quedará corriendo y esperando tareas. Déjalo abierto en esta terminal.

### 7. Ejecutar scrapers desde el frontend

Abre el frontend en http://localhost:5173 y haz clic en los botones de play (▶) de cada portal para ejecutar los scrapers.

## Comandos útiles

### Ver tareas en cola
```powershell
celery -A core.worker.celery_app inspect active
```

### Limpiar cola de tareas
```powershell
celery -A core.worker.celery_app purge
```

### Detener el worker
Presiona `Ctrl+C` en la terminal donde está corriendo.

## Troubleshooting

### Error: "No module named 'celery'"
**Solución:** Asegúrate de tener el entorno virtual activado:
```powershell
.\venv\Scripts\Activate.ps1
```

### Error: "Connection refused" a PostgreSQL
**Solución:** Verifica que el túnel SSH esté activo:
```powershell
Test-NetConnection localhost -Port 5433
```

### Error: "Connection refused" a Redis
**Solución:** Verifica que el túnel SSH esté activo:
```powershell
Test-NetConnection localhost -Port 6380
```

### Los scrapers no guardan datos
**Solución:** Verifica las variables de entorno:
```powershell
echo $env:POSTGRES_HOST
echo $env:REDIS_URL
```
