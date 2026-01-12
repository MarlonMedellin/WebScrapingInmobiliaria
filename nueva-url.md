# Portales Inmobiliarios para Integrar (Solo Arriendo Residencial)

Este archivo contiene la investigación de nuevos portales para expandir el sistema de monitoreo. Todas las URLs están configuradas para **Arriendo** y tipos residenciales (**Apartamento, Apartaestudio, Casa, Loft**) en Medellín.

## Lista de URLs de Búsqueda (Refinadas)

1. **Escala Inmobiliaria:** `https://escalainmobiliaria.com.co/inmuebles/g/arriendo/t/apartamentos/c/medellín/`
2. **Portofino Propiedad Raíz:** `https://portofinopropiedadraiz.com/resultados-de-busqueda/?Servicio=1&TipoInmueble=1247&Municipio=1`
3. **Arrendamientos Santa Fe:** `https://arrendamientossantafe.com/propiedades/?bussines_type=Arrendar&real_estate_type=Apartamento`
4. **Arrendamientos Ayurá:** `https://www.arrendamientosayura.com/buscar?iku5-id_type=0&iku5-city__id=4` (Nota: Requiere filtrar por tipo en el scraper si no funciona por URL)
5. **Su Vivienda:** `https://www.suvivienda.com.co/inmuebles/Arriendo/Apartamento/Medellín/`
6. **Arrendamientos La Aldea:** `https://www.arrendamientoslaaldea.com.co/inmuebles/Arriendo/clases_Apartamento/municipios_Medellín`
7. **Arrendamientos Nutibara:** `https://anutibara.com/search/inmueble/arriendo/medellin`

---

# Análisis Técnico por Portal

### 1. Escala Inmobiliaria
- **Estado:** ✅ Apta para scraping (Fácil)
- **URL Base:** `https://escalainmobiliaria.com.co/inmuebles/g/arriendo/t/apartamentos/c/medellín/`
- **Paginación:** Parámetro `?pagina=X` (ej. `?pagina=2`)
- **Datos Extraíbles:** Precio, Área (m²), Ubicación (Barrio/Ciudad), Habitaciones, Baños y Fotos.
- **Notas Técnicas:** Los datos son visibles directamente en los cards del listado (`.vi-cont-card`). Estructura DOM limpia.

### 2. Portofino Propiedad Raíz
- **Estado:** ✅ Apta para scraping (Intermedio)
- **URL Base:** `https://portofinopropiedadraiz.com/resultados-de-busqueda/?Servicio=1&TipoInmueble=1247&Municipio=1`
- **Paginación:** Basada en AJAX (Botón "Siguiente"). El parámetro `?pagina=X` no es 100% confiable. Se recomienda usar Playwright para interactuar con `#nextPage`.
- **Datos Extraíbles:** Título (`p.rojo`), Precio (`span.parse-float`), Ubicación, Área, Habitaciones y Baños.
- **Notas Técnicas:** Los datos están dentro de `div.caja.movil-25`.

### 3. Arrendamientos Santa Fe
- **Estado:** ✅ Apta para scraping (Fácil)
- **URL Base:** `https://arrendamientossantafe.com/propiedades/?bussines_type=Arrendar&real_estate_type=Apartamento`
- **Paginación:** Parámetro `?page=X` (ej. `?page=2&bussines_type=Arrendar`).
- **Datos Extraíbles:** Referencia (`.id`), Precio (contiene `$`), Área (`.area`), Alcobas (`.alcobas`), Garajes (`.garaje`).
- **Notas Técnicas:** Estructura muy limpia. Los datos técnicos tienen clases específicas, facilitando la extracción.

### 4. Arrendamientos Ayurá
- **Estado:** ✅ Apta para scraping (Intermedio)
- **URL Base:** `https://www.arrendamientosayura.com/buscar?iku5-id_type=0&iku5-city__id=4`
- **Paginación:** Botones "Sig." y "Ant.".
- **Datos Extraíbles:** Código (`#XXXXX`), Precio (`$`), Ubicación (Barrio), Habitaciones, Baños y Área.
- **Notas Técnicas:** Utiliza IDs dinámicos. Se recomienda buscar por contenido de texto (ej. "Área:") o selectores de jerarquía.

### 5. Su Vivienda
- **Estado:** ✅ Apta para scraping (Fácil)
- **URL Base:** `https://www.suvivienda.com.co/inmuebles/Arriendo/Apartamento/Medellín/`
- **Paginación:** Patrón de URL `/P/X/` (ej. `/P/2/`).
- **Datos Extraíbles:** Título (`.property_head h3 a`), Precio (`.favroute2 p`), Área (`.property_meta span:nth-child(1)`), Habitaciones (`.property_meta span:nth-child(2)`), Ubicación (`.proerty_content h3`).
- **Notas Técnicas:** Estructura consistente (`.property_item`). El precio está en un contenedor azul distintivo.

### 6. Arrendamientos La Aldea
- **Estado:** ✅ Apta para scraping (Fácil)
- **URL Base:** `https://www.arrendamientoslaaldea.com.co/inmuebles/Arriendo/clases_Apartamento/municipios_Medellín`
- **Paginación:** Elemento `.pagination` con enlaces numéricos y "Siguiente".
- **Datos Extraíbles:** Precio (`.listing-price`), Título (`h3`), Ubicación (`address`), Área y detalles.
- **Notas Técnicas:** Estructura de grid estándar. Fácil de procesar.

### 7. Arrendamientos Nutibara
- **Estado:** ✅ Apta para scraping (Intermedio)
- **URL Base:** `https://anutibara.com/search/inmueble/arriendo/medellin`
- **Paginación:** Parámetro `?pagina=X`.
- **Datos Extraíbles:** Título (`.title`), Precio, Sector/Barrio, Área e ID.
- **Notas Técnicas:** La URL es robusta para Medellín en general. El filtrado por tipo (Apartamento/Casa) puede requerir validación adicional en el scraper.

---

## Tipos Residenciales Incluidos
Para la integración, los scrapers deben buscar y clasificar los siguientes tipos:
- **Apartamento**
- **Apartaestudio**
- **Casa**
- **Apartamento Loft** (Especialmente en Su Vivienda)

## Criterios de Filtrado (Global)
Según `backend/scrapers/config.py`:
- **Operación:** Arriendo (Rent)
- **Precio Máximo:** $3,000,000 COP (Ajustable)
- **Barrios Objetivo:** Santa Fe, San Pablo, Campo Amor.
