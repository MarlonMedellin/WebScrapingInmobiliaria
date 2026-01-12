
https://escalainmobiliaria.com.co/inmuebles/g/arriendo/
https://portofinopropiedadraiz.com/resultados-de-busqueda/?Codigo=&TipoInmueble=1253&Servicio=1&Departamento=5&Municipio=1
https://arrendamientossantafe.com/propiedades/?bussines_type=Arrendar
https://www.arrendamientosayura.com/buscar?iku5-id_type=1&iku5-city__id=4
https://www.suvivienda.com.co/inmuebles/Arriendo/Apto-Loft/Medell%C3%ADn/
https://www.arrendamientoslaaldea.com.co/inmuebles/Arriendo/
https://anutibara.com/

#URL validadas

### Escala Inmobiliaria
- **Estado:** ✅ Apta para scraping (Fácil)
- **URLs Base:**
  - **Arriendo:** `https://escalainmobiliaria.com.co/inmuebles/g/arriendo/`
  - **Venta:** `https://escalainmobiliaria.com.co/inmuebles/g/venta/`
- **Paginación:** Parámetro `?pagina=X` (ej. `?pagina=2`)
- **Datos Extraíbles:** Precio, Área (m²), Ubicación (Barrio/Ciudad), Habitaciones, Baños y Fotos.
- **Notas Técnicas:** Los datos son visibles directamente en los cards del listado (`.vi-cont-card`). Estructura DOM limpia.
### Portofino Propiedad Raíz
- **Estado:** ✅ Apta para scraping (Intermedio)
- **URLs Base:**
  - **Arriendo:** `https://portofinopropiedadraiz.com/resultados-de-busqueda/?Servicio=1`
  - **Venta:** `https://portofinopropiedadraiz.com/resultados-de-busqueda/?Servicio=2`
- **Paginación:** Basada en AJAX (Botón "Siguiente"). El parámetro `?pagina=X` no es confiable. Se requiere interacción con `#nextPage`.
- **Datos Extraíbles:** Título (`p.rojo`), Precio (`span.parse-float`), Ubicación, Área, Habitaciones y Baños.
- **Notas Técnicas:** Los datos están dentro de `div.caja.movil-25`. Requiere un driver que maneje JavaScript para la paginación.

### Arrendamientos Santa Fe
- **Estado:** ✅ Apta para scraping (Fácil)
- **URLs Base:**
  - **Arriendo:** `https://arrendamientossantafe.com/propiedades/?bussines_type=Arrendar`
  - **Venta:** `https://arrendamientossantafe.com/propiedades/?bussines_type=Venta`
- **Paginación:** Parámetro `?page=X` (ej. `?page=2&bussines_type=Arrendar`).
- **Datos Extraíbles:** Referencia (`.id`), Precio (contiene `$`), Área (`.area`), Alcobas (`.alcobas`), Garajes (`.garaje`).
- **Notas Técnicas:** Estructura muy limpia y predecible. Los datos técnicos tienen clases específicas, lo que facilita mucho la extracción sin regex complejos.

### Arrendamientos Ayurá
- **Estado:** ✅ Apta para scraping (Intermedio)
- **URLs Base:**
  - **Arriendo:** `https://www.arrendamientosayura.com/buscar?iku5-id_type=0&iku5-city__id=4`
  - **Venta:** `https://www.arrendamientosayura.com/buscar?iku5-id_type=1&iku5-city__id=4`
- **Paginación:** Botones "Sig." y "Ant.". Requiere interacción o descifrar el parámetro de página si existe (no evidente en la URL simple).
- **Datos Extraíbles:** Código (`#XXXXX`), Precio (`$`), Ubicación (Barrio), Habitaciones, Baños y Área.
- **Notas Técnicas:** Utiliza IDs que parecen auto-generados (`i8lyns`, `iz9dp`). Se recomienda buscar por contenido de texto (ej. "Área:") o selectores de jerarquía relativos al card principal.

### Su Vivienda
- **Estado:** ✅ Apta para scraping (Fácil)
- **URLs Base:**
  - **Arriendo:** `https://www.suvivienda.com.co/inmuebles/Arriendo/Apartamento/Medellín/`
  - **Venta:** `https://www.suvivienda.com.co/inmuebles/Venta/Apartamento/Medellín/`
- **Paginación:** Patrón de URL `/P/X/` (ej. `/P/2/`). También tiene enlaces numéricos en el footer de los resultados.
- **Datos Extraíbles:** Título (`.property_head h3 a`), Precio (`.favroute2 p`), Área (`.property_meta span:nth-child(1)`), Habitaciones (`.property_meta span:nth-child(2)`), Ubicación (`.proerty_content h3`).
- **Notas Técnicas:** Estructura de clases muy consistente (`.property_item`). El precio está en un contenedor azul distintivo al final del card.

### Arrendamientos La Aldea
- **Estado:** ✅ Apta para scraping (Fácil)
- **URLs Base:**
  - **Arriendo:** `https://www.arrendamientoslaaldea.com.co/inmuebles/Arriendo/`
  - **Venta:** `https://www.arrendamientoslaaldea.com.co/inmuebles/Venta/`
- **Paginación:** Elemento `.pagination` con enlaces numéricos y "Siguiente".
- **Datos Extraíbles:** Precio (`.listing-price` o span dentro de `.listing-img-container`), Título (`h3` o `.listing-title`), Ubicación (`.listing-address` o `address`), Área y detalles.
- **Notas Técnicas:** Estructura de grid muy estándar. Fácil de procesar.

---
