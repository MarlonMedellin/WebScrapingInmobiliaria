---
description: Flujo de trabajo para Deep Scraping Local masivo con VPN
---

# Deep Scrape Local Workflow

Este flujo permite la descarga masiva de inmuebles utilizando la IP local (VPN) y sincronización posterior con el VPS.

## 1. Preparación de Base de Datos
Descargar la última versión de producción y levantar la DB local.

```powershell
docker compose -f docker-compose.db.yml up -d
.\dump_vps.bat
cmd /c "type vps_dump_clean.sql | docker exec -i local_postgres_dump psql -U admin realestate_db"
```

## 2. Ejecución del Barrido
⚠️ **REQUIERE VPN ACTIVA**

Ejecuta el seeder para el portal deseado. Si hay bloqueo, cambia de IP y presiona ENTER.

```powershell
# Ejemplo para Alberto Alvarez
$env:POSTGRES_HOST='localhost'; $env:POSTGRES_PORT='5432'; ..\backend\venv\Scripts\python.exe backend/local_seeder.py --portal albertoalvarez --max-pages 1000 --visible
```

## 3. Sincronización con Producción
Una vez finalizado el barrido, subir los nuevos datos al VPS.

```powershell
.\sync_up_vps.bat
```
