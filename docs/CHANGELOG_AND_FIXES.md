# Registro de Cambios y Correcciones (Changelog)

Este documento registra las correcciones críticas, sesiones de debugging, hitos históricos y reportes de pruebas.

---

## 📅 Historial de Hitos (Roadmap)

### [2026-01-11] Fase 10: Producción y Despliegue ✅
- **Despliegue en VPS:** Ubuntu 24.04 (IP: 168.231.64.247).
- **Dominio:** `csimedellin.link` con SSL vía Cloudflare.
- **Gateway:** Nginx configurado como Reverse Proxy.
- **Persistencia:** Volúmenes Docker para PostgreSQL y Redis.

### [2026-01-14] Fase 3: Clasificación Estática de Sectores ✅
- **Arquitectura:** Migración de filtrado dinámico (texto) a estático (`sector` col).
- **Normalización:** Sistema de "Nombre Bonito" vs "Sector Oficial".
- **Resolución Geográfica:** Fix definitivo para el falso positivo de "Santa Fe de Antioquia" en filtros de Guayabal.
- **Migración:** Script de actualización masiva para 2639 registros.

### [2026-01-10] Fase 6: Optimización Estricta ✅
- **Filtrado Pre-Guardado:** Rechazo automático de propiedades > $2.2M o fuera de zonas objetivo.
- **Early Stopping:** Parada tras 10 registros repetidos.
- **Freshness Badges:** Indicadores visuales de "Nuevo" (Verde) vs "Antiguo" (Gris).

### [2025-12-XX] Fase 1-5: Construcción del Núcleo ✅
- **Core:** 17 Portals integrados.
- **UI:** Dashboard React con filtros avanzados.
- **Actions:** Integración WhatsApp y archivado lógico.

---

## 🛠️ Correcciones Recientes (Hotfixes)

### [2026-01-13] Recuperación y Corrección de Monserrate Scraper
**Problema:** Extracción de IDs internos de WooCommerce en lugar de valores numéricos.
**Solución:** 
- Ajuste de selectores en `monserrate.py` (`table.shop_attributes`).
- Migración de datos corregidos Local -> VPS vía túnel SSH.

### [2026-01-14] Precisión Geográfica (Static Sectors)
**Problema:** Búsquedas por texto traían inmuebles de pueblos lejanos si el nombre del barrio coincidía (ej: "Santa Fe").
**Solución:** 
- Implementación de columna `sector` en el modelo `Property`.
- Uso de `neighborhood_map.json` como fuente de verdad única en tiempo de scraping.
- Reemplazo de `LIKE %neighborhood%` por `= :sector` en la API.

### [2026-01-12] Infraestructura y Seguridad
**Cambios:** API Key (`X-API-Key`), Rate Limiting (5 req/min), y limpieza automática con Celery Beat.

---

## 🧪 Reportes de Verificación

### [2026-01-12] Verificación de Entorno Local
**Estado:** ✅ APROBADO (8/8 Pruebas Exitosas)

**Componentes Verificados:**
1.  **Backend/Frontend:** Conexión híbrida (Local App -> VPS Data) funcionando 100%.
2.  **Túneles SSH:** Puertos 5433 (PG) y 6380 (Redis) estables.
3.  **Scripts:** `start-local-dev`, `check-tunnels`, `deploy-to-vps` operacionales.

**Limitación Conocida:**
⚠️ El Worker de Celery no puede ejecutarse dentro de Docker en Windows debido a restricciones de red con el host. Se debe ejecutar vía `venv`.
