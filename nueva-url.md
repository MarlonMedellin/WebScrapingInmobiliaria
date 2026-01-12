# Portales Inmobiliarios para Integrar (Solo Arriendo Residencial)

Este archivo contiene la investigación de nuevos portales para expandir el sistema de monitoreo.

## 📊 Estado de Integración

| Portal | Estado | Notas |
| :--- | :--- | :--- |
| Escala Inmobiliaria | ✅ | Implementado y auditado. Sensible a acentos. |
| Su Vivienda | ✅ | Implementado. Requiere acento en `Medellín` en la URL. |
| Portofino | ✅ | Implementado. Usa estructura Arrendasoft. |
| Arrendamientos Nutibara | ⏳ | Pendiente investigación DOM profunda. |
| Arrendamientos La Aldea | ⏳ | Pendiente. |
| Arrendamientos Santa Fe | ⏳ | Pendiente. |
| Arrendamientos Ayurá | ⏳ | Pendiente (Requiere filtrado por código). |

---

## 🛠️ Detalles por Portal

### 1. Escala Inmobiliaria ✅
- **URL Base:** `https://escalainmobiliaria.com.co/inmuebles/g/arriendo/t/apartamentos/c/medellín/`
- **Paginación:** `?pagina=X`
- **Selector Card:** `.card.card-space`
- **Selector Precio:** `h4` (dentro de link title="Valor propiedad")

### 2. Portofino Propiedad Raíz ✅
- **URL Base:** `https://portofinopropiedadraiz.com/resultados-de-busqueda/?Servicio=1&TipoInmueble=1247&Municipio=1`
- **Paginación:** `&Pagina=X` (Estructura Arrendasoft)
- **Selector Card:** `a[href*="detalle-propiedad"]`
- **Selector Precio:** `.body .contenedor2 p span.parse-float`

### 3. Su Vivienda ✅
- **URL Base:** `https://www.suvivienda.com.co/inmuebles/Arriendo/Apartamento/Medellín/`
- **Paginación:** `/X` (al final de la URL)
- **Selector Card:** `.property_item`
- **Selector Precio:** `.favroute2 p`

### 4. Arrendamientos Nutibara ⏳
- **URL Base:** `https://anutibara.com/search/inmueble/arriendo/medellin`
- **Paginación:** `?pagina=X`
- **Notas:** Pendiente validar selectores exactos de características.

---

## ⚡ Criterios Globales (Refinados)
- **Área Geográfica:** Valle de Aburrá extendido (Medellín, Envigado, Itagüí, Sabaneta, La Estrella).
- **Filtrado:** Broad Scraping + API Mapping (`neighborhood_map.json`).
- **Precio Máx:** $5,000,000 COP.
