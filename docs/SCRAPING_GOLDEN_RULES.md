# Scraping Golden Rules and Portal Directory

This document defines the strict operational rules for each portal integration and provides a directory of all active scrapers.

## Global Rules
1.  **Local Execution Only**: Scrapers must be triggered via `celery worker` in a local `venv`, never inside Docker on Windows.
2.  **Strict Filtering**: All scrapers must respect `backend/scrapers/config.py` for price and zone limits *before* saving to DB.
3.  **Early Stopping**: Scrapers initiate a stop sequence after encountering **10 consecutive existing properties**.

---

## 📊 Directory of Integrated Portals

| # | Portal | ID | Inmuebles | Technical Notes / Golden URLs |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Alberto Álvarez** | `albertoalvarez` | 211 | Extracción vía JSON estructurado (`textarea.field-property`). |
| 2 | **Ayurá** | `ayura` | 148 | Basado en atributos CMS (`cms-field-var`). |
| 3 | **Su Vivienda** | `suvivienda` | 52 | Paginación por path. Sensible a acentos. |
| 4 | **La Aldea** | `laaldea` | 29 | Paginación con doble slash (`//`). |
| 5 | **Conquistadores** | `conquistadores` | 27 | Gestión de barrios en Medellín. |
| 6 | **Nutibara** | `nutibara` | 19 | Nuxt.js / Carga dinámica. |
| 7 | **Protebienes** | `protebienes` | 60 | URL: `.com/inmuebles/Arriendo/X`. |
| 8 | **Integridad** | `integridad` | 258 | URL: `.com.co/inmuebles/Arriendo/X`. |
| 9 | **Escala** | `escalainmobiliaria` | 9 | Selector `.card.card-space`. |
| 10 | **La Castellana** | `lacastellana` | 23 | URL: `s/{type}/alquileres?page=N`. |
| 11 | **Santa Fe** | `santafe` | 1156 | URL: `?page=X&&bussines_type=Arrendar`. |
| 12 | **Portofino** | `portofino` | 3 | Estructura Arrendasoft. |
| 13 | **Finca Raíz** | `fincaraiz` | 2 | Crawler limitado. URL `/arriendo/`. |
| 14 | **El Castillo** | `elcastillo` | 488+ | Infinite Scroll (6s wait) + Location auto-append. |
| 15 | **Panda** | `panda` | 63 | SPA Interactions (Filters + JS Pagination). |
| 16 | **Monserrate** | `monserrate` | ~24 | WooCommerce. Extract from `table.shop_attributes`. |
| 17 | **Aportal** | `aportal` | 0 | Implementado. |

---

## Portal-Specific Implementation Rules

### 1. Arrendamientos Monserrate (`monserrate.py`)
*   **URL Strategy**: Iterates `/product-category/arrendamiento/page/{n}/`.
*   **Data Extraction**:
    *   **Grid**: Title, Price, Link.
    *   **Detail Page**: MUST parse `table.shop_attributes` to get accurate Area (m²), Bedrooms, and Bathrooms.
*   **Stop Condition**: 404 Page or empty `.products` list.

### 2. Arrendamientos El Castillo (`elcastillo.py`)
*   **Infinite Scroll**: Uses `window.scrollTo` loop.
*   **Timing**: REQUIRED wait of **6 seconds (6000ms)** after each scroll to allow lazy-loading.
*   **Location Fix**: Must append ", Medellín" to neighborhood names (e.g., "BELEN -> BELEN, Medellín").
*   **Field Cleaning**: Ignore `garage` field.

### 3. Fincaraiz (`fincaraiz.py`)
*   **URL Strategy**: Uses a single URL with query params: `?precioHasta={max_price}`.
*   **Zone Logic**: Does NOT filter by zone in the URL. Scrapes "Medellín" broadly and relies on `BaseScraper` to filter.
*   **Scroll**: Fixed scroll depth defined in `SEARCH_CRITERIA`.

### 4. General Maintenance
*   **Selectors**: When fixing broken scrapers, prefer `data-testid` or specific attribute selectors.
*   **User Agent**: Rotate User-Agents if 403 errors occur.
