---
description: Valida e integra un nuevo portal inmobiliario (E2E)
---

# 🚀 Workflow: Validación e Integración de Portal

Este flujo automatiza la inclusión de un nuevo portal desde la investigación hasta el despliegue en producción.

## Fase 1: Investigación y Validación
1. **Navegación:** Acceder a la URL especificada en `nueva-url.md`.
2. **Análisis DOM:** Identificar selectores CSS para:
   - Contenedor del card de propiedad.
   - Título, Precio, Ubicación, Área, Habitaciones.
   - Paginación (URL param o Click).
3. **Refinamiento:** Actualizar `nueva-url.md` con los selectores exactos y notas técnicas.

## Fase 2: Implementación Backend
1. **Crear Scraper:** Generar `backend/scrapers/[nombre].py` heredando de `BaseScraper`.
   - Implementar el método `async def scrape(self)`.
   - Usar `self.process_property(data)` para cada item.
2. **Registrar en Factory:** 
   - Importar la nueva clase en `backend/scrapers/factory.py`.
   - Agregar el caso correspondiente en `get_scraper` y en `get_all_scrapers`.

## Fase 3: Integración Frontend
1. **Actualizar App.jsx:**
   - Añadir el identificador del portal al array `PORTALS` en `frontend/src/App.jsx` para que aparezca la tarjeta en el dashboard.

## Fase 4: Despliegue (Turbo)
// turbo-all
1. **Commit & Push:**
   - `git add .`
   - `git commit -m "Integración completa de portal: [Nombre]"`
   - `git push origin main`
2. **VPS Deployment (vía SSH):**
   - Conectar al VPS: `ssh vps-scraping`
   - Actualizar repo: `cd /root/WebScrapingInmobiliaria && git pull origin main`
   - Reiniciar servicios: `docker compose restart worker backend`

---
**Instrucción para el Agente:** 
Para ejecutar este flujo, lee la información de `nueva-url.md`. Si un portal tiene el estado ⏳ (Pendiente), inicia desde la Fase 1. Si ya tiene ✅, inicia desde la Fase 2.
