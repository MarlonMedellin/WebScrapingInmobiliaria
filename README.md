# Medellín Real Estate Monitor 🏠🚀

Un sistema avanzado de web scraping y monitoreo inmobiliario diseñado para recolectar, centralizar y analizar ofertas de arriendo en zonas específicas de Medellín (Santa Fe, San Pablo, Campo Amor).

## 🌟 Características Principales

### Scraping Inteligente
- **9 Portales Integrados:** Fincaraiz, El Castillo, Santa Fe, Panda, Integridad, Protebienes, La Castellana, Monserrate y Aportal
- **Filtrado Automático:** Solo guarda inmuebles que cumplan criterios estrictos:
  - Operación: Arriendo
  - Tipos: Apartamentos, Casas, Apartaestudios
  - Zonas: Santa Fe, San Pablo, Campo Amor
  - Precio máximo: $2,200,000 COP
- **Parada Temprana:** Detiene el scraping tras encontrar 10 inmuebles consecutivos ya indexados

### Arquitectura Robusta
- **Patrón Strategy + Factory:** Fácil extensión para nuevos portales
- **Procesamiento Asíncrono:** Celery + Redis para tareas en segundo plano
- **Base de Datos Optimizada:** PostgreSQL con tracking de cambios de precio y última visualización

### Interfaz Premium
- **Dashboard Interactivo:** React + Vite con diseño dark mode y glassmorphism
- **Indicador de Frescura:** Columna "Días" con badges de color (Nuevo/Reciente/Antiguo)
- **Filtros Avanzados:** Por portal, precio, área, búsqueda de texto
- **Acciones Rápidas:** WhatsApp pre-rellenado, vista detallada, archivar

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.12** con FastAPI
- **Playwright** para navegación automatizada
- **Celery** para procesamiento asíncrono
- **BeautifulSoup4** para parsing HTML
- **SQLAlchemy** + **PostgreSQL 16**

### Frontend
- **React 18** con Vite
- **Vanilla CSS** con variables CSS modernas
- **Diseño responsive** y accesible

### Infraestructura
- **Docker Compose** para orquestación
- **Redis** para cache y colas
- **Nginx** (opcional para producción)

## 🚀 Inicio Rápido

### Requisitos Previos
- Docker y Docker Compose instalados
- Git
- 8GB RAM mínimo recomendado

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/MarlonMedellin/WebScrapingInmobiliaria.git
   cd WebScrapingInmobiliaria
   ```

2. **Levantar los servicios:**
   ```bash
   docker-compose up -d --build
   ```

3. **Acceder a la aplicación:**
   - **Frontend:** http://localhost:5173
   - **Backend API:** http://localhost:8000
   - **Documentación API:** http://localhost:8000/docs

### Uso Básico

1. **Scraping Manual:** Haz clic en el botón ▶ de cualquier portal en el dashboard
2. **Actualizar Datos:** Usa el botón "↻ Actualizar Datos" para refrescar la tabla
3. **Filtrar:** Usa la barra de filtros para buscar por portal, precio, área o texto
4. **Ver Detalles:** Haz clic en el título de cualquier inmueble
5. **Contactar:** Usa el botón 📱 para abrir WhatsApp con mensaje pre-rellenado
6. **Archivar:** Marca inmuebles como vistos con el botón ✖

## 📊 Portales Integrados

| Portal | URL | Estado | Características |
|:---|:---|:---:|:---|
| **Fincaraiz** | fincaraiz.com.co | ✅ | Filtrado por URL + precio |
| **El Castillo** | arrendamientoselcastillo.com.co | ✅ | Filtrado Python |
| **Santa Fe** | arrendamientossantafe.com | ✅ | Extracción mejorada área/alcobas |
| **Panda** | pandainmobiliaria.com | ✅ | Filtrado Python |
| **Integridad** | integridad.com.co | ✅ | Filtrado Python |
| **Protebienes** | protebienes.com.co | ✅ | Filtrado Python |
| **La Castellana** | lacastellana.com.co | ✅ | Grids dinámicos |
| **Monserrate** | monserrate.com | ✅ | WooCommerce |
| **Aportal** | aportal.com.co | ✅ | Filtrado Python |

## 🏗️ Estructura del Proyecto

```
WebScrapingInmobiliaria/
├── backend/
│   ├── scrapers/
│   │   ├── base.py           # Clase base con filtrado estricto
│   │   ├── config.py         # Criterios de búsqueda centralizados
│   │   ├── factory.py        # Factory pattern
│   │   ├── fincaraiz.py      # Scraper Fincaraiz
│   │   ├── elcastillo.py     # Scraper El Castillo
│   │   └── ...               # Otros scrapers
│   ├── models.py             # Modelos SQLAlchemy
│   ├── crud.py               # Operaciones DB
│   ├── tasks.py              # Tareas Celery
│   ├── main.py               # API FastAPI
│   └── database.py           # Configuración DB
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PropertiesTable.jsx  # Tabla con columna "Días"
│   │   │   ├── PropertyModal.jsx    # Vista detallada
│   │   │   └── FiltersBar.jsx       # Barra de filtros
│   │   ├── App.jsx           # Dashboard principal
│   │   └── App.css           # Estilos premium
│   └── package.json
├── docker-compose.yml        # Orquestación de servicios
├── README.md                 # Este archivo
├── avance.md                 # Estado detallado del proyecto
└── prompt.md                 # Contexto para IA
```

## 🔧 Configuración Avanzada

### Modificar Criterios de Búsqueda

Edita `backend/scrapers/config.py`:

```python
SEARCH_CRITERIA = {
    "operation": "arriendo",
    "property_types": ["apartamento", "casa", "apartaestudios"],
    "neighborhoods": ["santa fe", "san pablo", "campo amor"],
    "max_price": 2200000,
    "scroll_depth": 10
}
```

### Ajustar Parada Temprana

En `backend/scrapers/base.py`, método `should_stop_scraping()`:
```python
def should_stop_scraping(self, consecutive_existing: int, max_consecutive: int = 10):
    # Cambiar max_consecutive para más/menos tolerancia
```

## 📈 Roadmap

- [x] **Fase 1-5:** Sistema de scraping con filtrado inteligente
- [x] **Fase 6:** Frontend con indicadores de frescura
- [ ] **Fase 7:** Analítica (Precio/m² promedio, tendencias)
- [ ] **Fase 8:** Notificaciones automáticas (Email/Telegram)
- [ ] **Fase 9:** Exportación a Excel/CSV
- [ ] **Fase 10:** Despliegue en VPS

## 🐛 Troubleshooting

### El backend no responde
```bash
docker-compose restart backend
docker-compose logs backend --tail=50
```

### El frontend no muestra cambios
```bash
docker-compose restart frontend
# Limpiar caché del navegador (Ctrl+Shift+R)
```

### Scrapers fallan
```bash
# Ver logs del worker
docker-compose logs worker --tail=100

# Probar scraper manualmente
docker-compose exec backend python -m scrapers.santafe
```

## 📝 Licencia

Este proyecto es de uso privado para análisis del mercado inmobiliario de Medellín.

---

**Desarrollado con ❤️ para optimizar la búsqueda de arriendo en Medellín**
