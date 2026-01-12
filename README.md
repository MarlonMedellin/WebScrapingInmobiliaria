# Medellín Real Estate Monitor 🏠🚀

Un sistema avanzado de web scraping y monitoreo inmobiliario diseñado para recolectar, centralizar y analizar ofertas de arriendo en zonas específicas de Medellín (Santa Fe, San Pablo, Campo Amor).

## 🌟 Características Principales

### Scraping Inteligente
- **9 Portales Integrados:** Fincaraiz, El Castillo, Santa Fe, Panda, Integridad, Protebienes, La Castellana, Monserrate y Aportal.
- **Filtrado Automático:** Solo guarda inmuebles que cumplan criterios estrictos:
  - Operación: Arriendo, Tipos: Apartamentos, Casas, Apartaestudios.
  - Zonas: Santa Fe, San Pablo, Campo Amor (filtrado estricto por barrio).
  - Precio máximo: $5,000,000 COP.
- **Parada Temprana:** Detiene el scraping tras encontrar 10 inmuebles consecutivos ya indexados para optimizar recursos.

### Arquitectura Robusta y Producción
- **Despliegue Profesional:** VPS Ubuntu 24.04 con Docker Compose y Nginx.
- **Gateway Nginx:** Configurado como reverse proxy en el puerto 80 con soporte para dominios personalizados.
- **Persistencia Total:** Volúmenes Docker para PostgreSQL y Redis, garantizando que los datos sobrevivan a reinicios.
- **Procesamiento Asíncrono:** Celery + Redis para ejecutar múltiples scrapings en paralelo sin bloquear la UI.

### Interfaz Premium (UX/UI)
- **Dashboard Dinámico:** React + Vite con diseño dark mode, glassmorphism y micro-animaciones.
- **Feedback en Tiempo Real:** Las tarjetas de portales muestran un estado de "pulsación" y un spinner (⏳) cuando hay una tarea de scraping activa.
- **API Híbrida:** Detección automática del entorno (Local vs Producción) para conectar con el backend correcto sin cambios manuales de código.
- **Indicador de Frescura:** Columna "Días" con badges de color (Nuevo/Reciente/Antiguo).

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.12** (FastAPI)
- **Playwright** (Navegación headless automatizada)
- **Celery + Redis** (Distribución de tareas)
- **SQLAlchemy + PostgreSQL 16** (Base de datos relacional)

### Frontend
- **React 18** (Vite + Vanilla CSS)
- **Nginx** (Proxy inverso y servidor de estáticos)

### Infraestructura
- **Docker Compose** (Orquestación completa)
- **Cloudflare** (SSL/HTTPS y gestión de DNS)

## 🚀 Acceso al Sistema

### Producción
- **Dominio:** [https://csimedellin.link](https://csimedellin.link)
- **Estado:** ✅ Online y Operativo

### Desarrollo Local
1. **Clonar e Instalar:**
   ```bash
   git clone https://github.com/MarlonMedellin/WebScrapingInmobiliaria.git
   docker-compose up -d --build
   ```
2. **Acceder:**
   - **Frontend:** http://localhost:5173
   - **Backend API:** http://localhost:8000

## 🏗️ Estructura del Proyecto

```
WebScrapingInmobiliaria/
├── backend/
│   ├── scrapers/         # Lógica de extracción (BaseScraper + 9 portales)
│   ├── core/             # Configuración de Celery
│   ├── main.py           # API principal
│   └── init_tables.py    # Script de inicialización de DB
├── frontend/
│   ├── src/App.jsx       # Dashboard con detección dinámica de API
│   └── vite.config.js    # Configuración de hosts permitidos
├── nginx.conf            # Configuración de Proxy Inverso para producción
└── docker-compose.yml    # Definición de servicios (db, redis, backend, worker, frontend, nginx)
```

## 📉 Roadmap

- [x] **Fase 1-5:** Sistema core de scraping con filtrado inteligente.
- [x] **Fase 6:** Frontend con indicadores de frescura y UI premium.
- [x] **Fase 10:** Despliegue en VPS con Nginx y dominio propio.
- [ ] **Fase 7:** Analítica (Precio/m² promedio, tendencias de mercado).
- [ ] **Fase 8:** Notificaciones automáticas (Telegram Bot / Email).
- [ ] **Fase 9:** Exportación masiva (Excel/CSV).

---
**Desarrollado para optimizar la toma de decisiones en el mercado inmobiliario de Medellín.**
