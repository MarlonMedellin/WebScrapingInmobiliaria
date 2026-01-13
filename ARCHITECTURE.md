# Arquitectura Técnica 🏗️

Este documento describe la arquitectura interna del sistema para facilitar el entendimiento de su funcionamiento por parte de desarrolladores e IAs.

## 🏗️ Resumen de Componentes

El sistema sigue una arquitectura de microservicios orquestada con **Docker Compose**:

1.  **Frontend (React + Vite):** Dashboard SPA para visualización, filtrado y disparo manual de tareas.
2.  **API (FastAPI):** Punto de entrada para el frontend, gestión de base de datos y encolamiento de tareas.
3.  **Worker (Celery):** Motor de procesamiento en segundo plano que ejecuta los scrapers usando **Playwright**.
4.  **Database (PostgreSQL 16):** Persistencia de inmuebles, estados y búsquedas guardadas.
5.  **Broker (Redis):** Cola de mensajes para Celery y caché temporal.
6.  **Proxy (Nginx):** Reverse proxy para producción, manejando el tráfico hacia el frontend y backend.

---

## 🕵️ Sistema de Scraping Inteligente

### 1. BaseScraper
Todos los scrapers heredan de una clase base (`backend/scrapers/base.py`) que estandariza:
- Inicialización de **Playwright** (User-Agents, Headless mode).
- Navegación con manejo de timeouts.
- **Procesamiento de Inmuebles:** Lógica base para decidir si un inmueble es nuevo, una actualización de precio o ya existe.
- **Detección de Parada:** Si encuentra $N$ registros consecutivos ya existentes, detiene el proceso para ahorrar recursos.

### 2. Estrategia de Mapeo Curado de Alta Precisión
A diferencia de los sistemas tradicionales, este monitor utiliza un enfoque de "Recolección Amplia y Clasificación Manual":
- **Nivel de Scraper:** Recolecta todo lo disponible en el Valle de Aburrá (Medellín, Envigado, Itagüí, Sabaneta, La Estrella) para no perder datos por variaciones de texto.
- **Mapeo de Barrios (`neighborhood_map.json`):** Archivo maestro curado manualmente con +200 variantes mapeadas a barrios estándar. Utiliza un orden de precedencia estricto para evitar colisiones entre barrios con nombres similares en diferentes comunas.
- **Normalización en Base de Datos:** Los inmuebles se procesan mediante `neighborhood_utils.py` para asignar un valor al campo `neighborhood_resolved`, que es el único utilizado para el filtrado en el Dashboard, garantizando precisión absoluta.

---

## 🗃️ Modelo de Datos

### Propiedades (`Property`)
- **Campos principales:** Título, precio, ubicación, link, imagen, fuente, área, habitaciones, baños.
- **Estados:** `NEW` (recién descubierto), `SEEN` (visto), `ARCHIVED` (descartado), `FAVORITE` (destacado).
- **Indicador de Frescura:** Calculado en tiempo real comparando la fecha de creación con la fecha actual.

---

## 🚀 Flujo de Despliegue (VPS)

El despliegue está automatizado mediante un script de PowerShell y un flujo de Git:
1.  **Local:** Ajustes de código y commits.
2.  **GitHub:** Push a `main`.
3.  **VPS (CI/CD Manual):** `git pull` + `docker compose restart`.
4.  **Infraestructura:** VPS Ubuntu 24.04 con Docker.

---

## 🛠️ Extensibilidad

Para añadir un nuevo portal inmobiliario:
1.  Investigar selectores en `nueva-url.md`.
2.  Crear clase en `backend/scrapers/`.
3.  Registrar en `backend/scrapers/factory.py`.
4.  Añadir a la lista de `PORTALS` en `frontend/src/App.jsx`.
5.  Actualizar la lista blanca en el endpoint `/scrape` de `backend/main.py`.

---

## 🤖 Workflows Automatizados (Agentic Flows)

El proyecto incluye flujos de trabajo en `.agent/workflows/` para automatizar tareas repetitivas:
- **`/validar-url`:** Un flujo E2E que valida un portal, crea el código del scraper, lo integra en el frontend y lo despliega en el VPS automáticamente.
- **`/setup-local-dev`:** Configura túneles SSH hacia el VPS para usar la base de datos de producción desde el entorno local.
- **`/git-update`:** Automatiza el ciclo de add, commit, push y actualización del VPS.
