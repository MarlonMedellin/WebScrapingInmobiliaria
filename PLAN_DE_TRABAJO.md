# PLAN DE TRABAJO - Medellín Real Estate Monitor

Este documento define la hoja de ruta para la construcción del monitor inmobiliario, siguiendo una **Estrategia de Desarrollo Iterativo**.

## 🚀 Estrategia de Ejecución
- **No se avanza de fase** hasta que la actual esté completada y validada.
- **Validación continua:** Cada fase debe ser funcional por sí misma.
- **Infraestructura:** Todo corre sobre Docker para paridad entre Dev y Prod.

---

## 📅 Fases del Proyecto

### ✅ FASE DE PREPARACIÓN (ACTUAL)
- **Entregables:** `docker-compose.yml`, Estructura de carpetas, Workflow definido.
- **Objetivo:** Tener los cimientos listos para empezar a construir.

### ⏳ FASE 1: MVP - Scraping Single-Site
**Objetivo:** Validar el flujo completo de datos (Scrape -> DB) con UN solo sitio.
- [ ] Configuración de servicios base (Postgres, Redis) en Docker.
- [ ] Backend (FastAPI) esqueleto inicial.
- [ ] Script de Playwright para `fincaraiz.com.co` (o similar).
- [ ] Extracción de datos clave: Título, Precio, Ubicación, Link.
- [ ] Persistencia en PostgreSQL.
- [ ] Validación de ejecución diaria y detección básica de nuevos items.

### ✅ FASE 2: Scraping Avanzado y Multi-Sitio
**Objetivo:** Escalar la capacidad de recolección de datos.
- [x] Refactorización a Patrón Strategy para soportar múltiples fuentes (`BaseScraper`).
- [x] **Multi-Sitio:** Añadir segundo portal (El Castillo).
- [x] **Integración Celery:** Ejecución asíncrona y colas de trabajo (`tasks.py`).
- [x] **Factory Manager:** Despacho dinámico de scrapers (`ScraperFactory`).
- [x] Gestión de anti-bot: Implementada vía headers y delays en BaseScraper.
- [x] Optimización de concurrencia: Habilitada mediante workers de Celery.

### ⏳ FASE 3: Interfaz de Usuario Inicial (ACTUAL)
**Objetivo:** Visualizar los datos recolectados.
- [x] Inicializar proyecto React + Vite.
- [x] API Endpoint: `GET /properties` con paginación.
- [ ] Configurar Nginx como Reverse Proxy (Postergado para Prod).
- [ ] Componente React: Tabla de propiedades.

### ⏳ FASE 4: Configuración y Filtros
**Objetivo:** Controlar el scraper desde la UI.
- [ ] UI para definir URLs objetivo y criterios de búsqueda.
- [ ] Endpoint para guardar configuración en DB.
- [ ] Filtros avanzados en el listado (Barrio, Precio, Metraje).

### ⏳ FASE 5: Integración de Acciones
**Objetivo:** Hacer la herramienta operativa para el negocio.
- [ ] Botón de WhatsApp con mensaje pre-rellenado.
- [ ] Vista de detalle del inmueble.

### ⏳ FASE 6: Analítica
**Objetivo:** Insights de mercado.
- [ ] Cálculos de Precio/m² promedio.
- [ ] Gráficos de tendencias históricos.

### ⏳ FASE 7: Exportación y Entrega
**Objetivo:** Portabilidad y documentación.
- [ ] Exportar data a CSV/Excel.
- [ ] Documentación de despliegue y mantenimiento.
- [ ] Transferencia final al VPS.

---

## 🛠 Stack Tecnológico Confirmado
- **Infraestructura:** Docker Compose.
- **Backend:** Python 3.12+ (FastAPI), Playwright, Celery.
- **Frontend:** React + Vite, TailwindCSS.
- **Base de Datos:** PostgreSQL 16 (Tuned for 8GB RAM).
- **Colas:** Redis (AOF Persistence).
