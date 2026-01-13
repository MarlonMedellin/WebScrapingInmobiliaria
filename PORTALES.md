# 🏘️ Directorio de Portales Integrados

Este archivo contiene la lista oficial de inmobiliarias y portales que alimentan el monitor de `csimedellin.link`.

## 📊 Estadísticas de Cobertura (Tiempo Real)

| # | Inmobiliaria / Portal | ID (source) | Inmuebles | Notas Técnicas |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Alberto Álvarez** | `albertoalvarez` | 211 | Extracción vía JSON estructurado. |
| 2 | **Arrendamientos Ayurá** | `ayura` | 148 | Basado en atributos CMS (`cms-field-var`). |
| 3 | **Su Vivienda** | `suvivienda` | 52 | Paginación por path. Sensible a acentos. |
| 4 | **Arrendamientos La Aldea** | `laaldea` | 29 | Paginación con doble slash (`//`). |
| 5 | **Conquistadores** | `conquistadores` | 27 | Nuevo - Gestión de barrios en Medellín. |
| 6 | **Arrendamientos Nutibara** | `nutibara` | 19 | Nuxt.js / Carga dinámica. |
| 7 | **Protebienes** | `protebienes` | 60 | **Golden URL:** `.com/inmuebles/Arriendo/X`. |
| 8 | **Integridad** | `integridad` | 258 | **Golden URL:** `.com.co/inmuebles/Arriendo/X`. |
| 9 | **Escala Inmobiliaria** | `escalainmobiliaria` | 9 | Selector `.card.card-space`. |
| 10 | **La Castellana** | `lacastellana` | 23 | **Golden URL:** `s/{type}/alquileres?page=N`. |
| 11 | **Arrendamientos Santa Fe** | `santafe` | 1156 | **Golden URL:** `?page=X&&bussines_type=Arrendar`. Selectores `.inner-card`. |
| 12 | **Portofino** | `portofino` | 3 | Estructura Arrendasoft. |
| 13 | **Finca Raíz** | `fincaraiz` | 2 | Crawler limitado. |
| 14 | **El Castillo** | `elcastillo` | 488+ | **Golden Logic:** Infinite Scroll (6s wait) + Location auto-append. |
| 15 | **Inmobiliaria Panda** | `panda` | 63 | **Golden Logic:** SPA Interactions (Filters + JS Pagination). |
| 16- [x] **Monserrate**
  - **Golden Logic**: WooCommerce structure. Data extracted reliably from `li` class attributes (`pa_area-X`, `pa_sector-Y`).
  - **URL**: `/product-category/arrendamiento/page/{n}/`
 |
| 17 | **Aportal** | `aportal` | 0 | Implementado. |

---

## 🛠️ Resumen Global
- **Total Portales:** 17 implementados.
- **Portales con Data:** 13 activos hoy.
- **Última Integración:** Conquistadores (12/01/2026).

## 📝 Notas de Mantenimiento
- Para disparar manualmente un scraper desde el VPS:
  `curl -X POST http://localhost:8000/scrape/[ID] -H 'X-API-Key: dev-secret-key'`
