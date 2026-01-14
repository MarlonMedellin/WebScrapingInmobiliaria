# Configuración del Entorno de Desarrollo Local

Este documento consolida el contexto técnico y operativo para el desarrollo local en el proyecto **WebScrapingInmobiliaria**, permitiendo trabajar con servicios locales conectados a datos de producción.

## 1. Arquitectura de Desarrollo Híbrido

Implementamos una arquitectura que conecta servicios locales (Frontend/Backend) con la infraestructura de datos del VPS mediante túneles seguros.

```mermaid
graph TD
    subgraph Local_Windows [Máquina Local (Windows)]
        FE[Frontend React] -->|:5173| BE[Backend FastAPI]
        BE -->|:8000| Tunnel_PG[Puerto Local 5433]
        
        subgraph Scripts_Tools
            Start[start-local-dev.ps1]
            Stop[stop-local-dev.ps1]
            Check[check-tunnels.ps1]
            Deploy[deploy-to-vps.ps1]
        end
    end

    subgraph SSH_Tunnel [Túneles SSH Encriptados]
        Tunnel_PG <==>|SSH| Remote_PG
        Tunnel_Redis[Puerto Local 6380] <==>|SSH| Remote_Redis
    end

    subgraph VPS_Linux [VPS Producción]
        Remote_PG[(PostgreSQL :5432)]
        Remote_Redis[(Redis :6379)]
        Worker[Celery Worker] --> Remote_Redis
        Worker --> Remote_PG
    end
```

## 2. Componentes Clave

| Componente | Local (Puerto) | VPS (Puerto) | Conexión | Notas |
|------------|----------------|--------------|----------|-------|
| **Frontend** | `localhost:5173` | Nginx:80 | N/A | Consume Backend Local |
| **Backend** | `localhost:8000` | `:8000` | Host | Se conecta a BD VPS vía túnel |
| **PostgreSQL** | `localhost:5433` | `:5432` | SSH Tunnel | Datos de Producción |
| **Redis** | `localhost:6380` | `:6379` | SSH Tunnel | Cola de tareas Celery |

---

## 3. Scripts de Automatización (Referencia)

Ubicación: Raíz del proyecto.

### 🚀 `start-local-dev.ps1`
**Uso:** `.\start-local-dev.ps1`
- Inicia túneles SSH.
- Verifica/Crea `.env.local`.
- Levanta Docker Compose (`docker-compose.local.yml`).

### 🛑 `stop-local-dev.ps1`
**Uso:** `.\stop-local-dev.ps1`
- Detiene contenedores Docker.
- Cierra procesos SSH.

### 🔍 `check-tunnels.ps1`
**Uso:** `.\check-tunnels.ps1`
- Diagnóstico de conectividad (Puertos 5433 y 6380).
- Lista procesos SSH activos.

### 🚢 `deploy-to-vps.ps1`
**Uso:** `.\deploy-to-vps.ps1 -CommitMessage "feat: mensaje"`
- Commit + Push a GitHub.
- SSH al VPS -> `git pull` -> `docker compose restart`.

---

## 4. Guía de Deep Scraping ("Sembrado Masivo")

Esta guía describe el protocolo para recolectar datos históricos masivos sin quemar la IP del servidor de producción, utilizando hardware local y VPN.

### Objetivo
Descargar masivamente miles de inmuebles (saltándose el límite de "ya vistos") usando IPs residenciales rotativas (VPN) y sincronizar con el VPS.

### Flujo de Trabajo
1.  **Bajada de Datos (Dump VPS)**:
    ```powershell
    .\dump_vps.bat
    # Descarga backup VPS -> Restaura en contenedor local
    ```
2.  **Barrido Local (Seeding)**:
    ```powershell
    # En directorio backend/
    $env:POSTGRES_HOST='localhost'; $env:POSTGRES_PORT='5432'; ..\backend\venv\Scripts\python.exe local_seeder.py --portal [NOMBRE] --max-pages 1000 --visible
    ```
    *Si te bloquean (403), cambia IP de VPN y reanuda.*
3.  **Subida de Datos (Sync VPS)**:
    ```powershell
    .\sync_up_vps.bat
    # Dump Local -> SCP -> Restore VPS -> Restart
    ```

---

## 5. Workflow de Scraping Diario (Golden Rule)

⚠️ **IMPORTANTE:** No ejecutar scrapers comunes dentro del contenedor Docker local. Usar siempre un entorno virtual (`venv`) en Windows para evitar problemas de red de Docker.

### Pasos Manuales:
1.  **Verificar túneles**: `Get-Process ssh`
2.  **Activar venv**: `cd backend; .\venv\Scripts\Activate.ps1`
3.  **Configurar Env**: `$env:POSTGRES_HOST="localhost"; ...`
4.  **Ejecutar Worker**: `celery -A core.worker.celery_app worker --loglevel=info`

### Migración de Datos (Sectores)
Si se añaden nuevos barrios al `neighborhood_map.json` o se cambia la estructura, ejecutar:
```powershell
venv\Scripts\python.exe backend\migrate_sectors.py
```
*Este script recalcula los sectores de todos los inmuebles existentes en la BD.*

---

## 6. Filosofía de Automatización (Antigravity Rules)

Para mantener el entorno ordenado, el agente sigue esta matriz de decisión:
*   **RULES (Automático):** Cosas que siempre deben pasar (ej. usar `docker-compose.local.yml`).
*   **WORKFLOWS (Manual):** Guías paso a paso complejas invocables por el usuario.
*   **SCRIPTS (Ejecutable):** Automatización total de tareas repetitivas (`start-local-dev`).
