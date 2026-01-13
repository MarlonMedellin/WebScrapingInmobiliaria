# 🚜 Guía de Deep Scraping Local

Esta guía describe el protocolo de **"Sembrado Masivo"** utilizado para recolectar datos históricos de portales inmobiliarios sin quemar la IP del servidor de producción, utilizando el hardware local y una VPN.

## 🎯 Objetivo
Descargar masivamente miles de inmuebles (saltándose el límite de "ya vistos") usando IPs residenciales rotativas (VPN) y luego sincronizar esa data con el servidor VPS.

## 🛠️ Prerrequisitos
1.  **Docker Desktop** (Corriendo en Windows).
2.  **VPN** con IPs de Colombia/Latam.
3.  **Túnel SSH** configurado (opcional, pero útil).

---

## 🔄 Flujo de Trabajo (Paso a Paso)

### 1. Preparar el Terreno (Bajada de Datos)
Antes de empezar, necesitamos la última versión de la base de datos de producción para no duplicar trabajo y mantener el mapeo de barrios.

Ejecutar el script:
```powershell
.\dump_vps.bat
# Esto descarga el backup del VPS al archivo local_postgres_dump
```

Luego, restaurar en el contenedor local:
```powershell
cmd /c "type vps_dump_clean.sql | docker exec -i local_postgres_dump psql -U admin realestate_db"
```

### 2. Ejecutar el Barrido (Seeding)
Con la base de datos lista, lanzamos el scraper en modo "Seed".

**Comando:**
```powershell
# En el directorio backend/
$env:POSTGRES_HOST='localhost'; $env:POSTGRES_PORT='5432'; ..\backend\venv\Scripts\python.exe local_seeder.py --portal [NOMBRE_PORTAL] --max-pages 1000 --visible
```

**Si te bloquean:**
1.  El script se pausará y dirá: `[!!!] BLOCK DETECTED...`
2.  Cambia tu IP en la VPN.
3.  Presiona ENTER en la terminal para reanudar.

### 3. Sincronizar con Producción (Subida)
Una vez tengas miles de registros nuevos en tu local, súbelos al VPS.

Ejecutar el script automatizado:
```powershell
.\sync_up_vps.bat
```
*Este script hace dump local -> sube por SCP -> restaura en VPS -> reinicia servicios.*

---

## 📂 Archivos Clave
- `backend/local_seeder.py`: Orquestador del scraping masivo.
- `sync_up_vps.bat`: Script de despliegue a producción.
- `docker-compose.db.yml`: Contenedor de base de datos local efímera.
