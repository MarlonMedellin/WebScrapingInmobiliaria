# Medellín Real Estate Monitor 🏠🚀

Un sistema avanzado de web scraping y monitoreo inmobiliario diseñado para recolectar, centralizar y analizar ofertas de arriendo en el Valle de Aburrá (Medellín, Envigado, Itagüí, Sabaneta, La Estrella).

## 🌟 Características Principales

### Scraping de Alta Disponibilidad
- **17 Portales Integrados:** Fincaraiz, El Castillo, Santa Fe, Panda, Integridad, Protebienes, La Castellana, Monserrate, Aportal, Escala Inmobiliaria, Su Vivienda, La Aldea, Nutibara, Portofino, Ayura, Alberto Álvarez y **Conquistadores**.
- **Recolección Masiva:** Captura todas las ofertas residenciales de las ciudades objetivo para garantizar que no se pierda ninguna oportunidad por variaciones en la nomenclatura.
- **Parada Temprana Inteligente:** Detiene el proceso automáticamente tras detectar 10 registros ya existentes para optimizar el ancho de banda y CPU.

### Curación de Alta Precisión y Mapeo
- **Mapeo de Barrios Manual:** Centralizado en `neighborhood_map.json`, optimizado mediante curación manual de más de 150 barrios para resolver colisiones (ej: San Pablo Comuna 1 vs Comuna 15).
- **Normalización en DB:** Campo `neighborhood_resolved` para garantizar que los filtros del Dashboard sean 100% precisos.
- **Filtros Avanzados en Dashboard:** Filtrado por precio (vía slider), área, portal, estado (Nuevo/Archivado) y barrios mapeados con alta precisión.

### Arquitectura Robusta
- **Dockerizado:** Entorno consistente para base de datos (PostgreSQL 16), cola de tareas (Redis) y worker.
- **Procesamiento Asíncrono:** Celery para navegación concurrente sin afectar la respuesta de la API.
- **Frontend Premium:** React + Vite con diseño moderno, micro-animaciones y feedback de scraping en tiempo real.
- **Seguridad y Control:** Implementación de API Key, Rate Limiting por IP para scrapers y CORS controlado.
- **Automatización de Limpieza:** Celery Beat para archivar automáticamente anuncios que no han sido vistos en 3 días.

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.12, FastAPI, Playwright, Celery, SQLAlchemy.
- **Frontend:** React 18, Vite, Vanilla CSS.
- **Infraestructura:** Docker Compose, PostgreSQL 16, Redis, Nginx (Reverse Proxy), Cloudflare.

## 🏗️ Estructura del Proyecto

```
WebScrapingInmobiliaria/
├── backend/
│   ├── scrapers/            # Motores de extracción (Escala, Fincaraiz, etc.)
│   ├── neighborhood_map.json  # Mapeo de barrios (Clave: Valor)
│   ├── discovered_neighborhoods.json # Barrios nuevos detectados
│   ├── core/                # Configuración de Celery y Broker
│   └── main.py              # API con lógica de filtrado inteligente
├── frontend/
│   ├── src/App.jsx          # Dashboard central interactivo
│   └── src/components/      # Componentes de filtrado y visualización
├── ARCHITECTURE.md          # Detalles técnicos profundos
└── docker-compose.yml       # Orquestación de servicios
```

## 🚀 Despliegue

### Producción
- **URL:** [https://csimedellin.link](https://csimedellin.link)
- **Deployment:** Automatizado vía Git y SSH al VPS.

### Desarrollo Local
1.  Asegurar tener Docker instalado.
2.  Ejecutar `docker-compose up -d --build`.
3.  Acceder a `http://localhost:5173`.

### Configuración de Variables de Entorno (.env)
El sistema utiliza las siguientes variables clave:
- `API_KEY`: Llave para autorizar acciones críticas (scrape, borrar búsquedas, etc).
- `ALLOWED_ORIGINS`: Dominios permitidos por CORS (ej: `https://tu-dominio.com,http://localhost:5173`).
- `REDIS_URL`: Conexión al broker de Celery.
- `POSTGRES_SHARED_BUFFERS`: RAM asignada a la base de datos (ej: `2GB`).
- `VITE_API_KEY`: (Frontend) Debe coincidir con `API_KEY`.

---
**Desarrollado para optimizar la toma de decisiones en el mercado inmobiliario de Medellín.**
