# 🏘️ Directorio de Portales Integrados

Este archivo contiene la lista oficial de inmobiliarias y portales que alimentan el monitor de `csimedellin.link`.

## 📊 Estadísticas de Cobertura (Tiempo Real)

| # | Inmobiliaria / Portal | ID (source) | Inmuebles | Notas Técnicas |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Alberto Álvarez** | `albertoalvarez` | 211 | Extracción vía JSON estructurado. |
| 2 | **Arrendamientos Ayurá** | `ayura` | 148 | Basado en atributos CMS (`cms-field-var`). |
| 3 | **Su Vivienda** | `suvivienda` | 52 | Paginación por path. Sensible a acentos. |
| 4 | **Arrendamientos La Aldea** | `laaldea` | 29 | Paginación con doble slash (`//`). |
| 5 | **Arrendamientos Nutibara** | `nutibara` | 19 | Nuxt.js / Carga dinámica. |
| 6 | **Protebienes** | `protebienes` | 16 | Implementado. |
| 7 | **Integridad** | `integridad` | 11 | Implementado. |
| 8 | **Escala Inmobiliaria** | `escalainmobiliaria` | 9 | Selector `.card.card-space`. |
| 9 | **La Castellana** | `lacastellana` | 8 | Implementado. |
| 10 | **Arrendamientos Santa Fe** | `santafe` | 8 | Paginación vía `?page=X`. |
| 11 | **Portofino** | `portofino` | 3 | Estructura Arrendasoft. |
| 12 | **Finca Raíz** | `fincaraiz` | 2 | Crawler limitado. |
| 13 | **El Castillo** | `elcastillo` | 0 | Implementado (Sin inmuebles actuales). |
| 14 | **Inmobiliaria Panda** | `panda` | 0 | Implementado. |
| 15 | **Monserrate** | `monserrate` | 0 | Implementado. |
| 16 | **Aportal** | `aportal` | 0 | Implementado. |

---

## 🛠️ Resumen Global
- **Total Portales:** 16 implementados.
- **Portales con Data:** 12 activos hoy.
- **Última Integración:** Alberto Álvarez (12/01/2026).

## 📝 Notas de Mantenimiento
- Para disparar manualmente un scraper desde el VPS:
  `curl -X POST http://localhost:8000/scrape/[ID] -H 'X-API-Key: dev-secret-key'`
