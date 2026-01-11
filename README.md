# Medellín Real Estate Monitor 🏠🚀

Un sistema avanzado de web scraping y monitoreo inmobiliario diseñado para recolectar, centralizar y analizar ofertas de múltiples portales en Medellín y el Valle de Aburrá.

## 🌟 Características

- **Scraping Multi-Portal:** Integración con 9 portales líderes (Finca Raíz, El Castillo, Santa Fe, Panda, Integridad, Protebienes, La Castellana, Monserrate y Aportal).
- **Arquitectura Robusta:** Basado en el patrón *Strategy* y *Factory* para añadir nuevas fuentes fácilmente.
- **Procesamiento Asíncrono:** Uso de Celery y Redis para manejar tareas de scraping en segundo plano sin bloquear la API.
- **Tecnología Moderna:** 
  - **Backend:** FastAPI (Python), Playwright (Navegación automatizada), SQLAlchemy (PostgreSQL).
  - **Frontend:** React + Vite, Diseño Premium con Glassmorphism y Dark Mode.
  - **Infraestructura:** Docker Compose para un despliegue sencillo y consistente.

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.12, FastAPI, Playwright, Celery, BeautifulSoup4.
- **Base de Datos:** PostgreSQL 16.
- **Cache/Task Queue:** Redis.
- **Frontend:** React (Vite).
- **Contenedores:** Docker & Docker Compose.

## 🚀 Inicio Rápido

### Requisitos Previos

- Docker y Docker Compose instalados.
- Git.

### Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/MarlonMedellin/WebScrapingInmobiliaria.git
   cd WebScrapingInmobiliaria
   ```

2. Levanta los servicios con Docker:
   ```bash
   docker-compose up -d --build
   ```

3. El sistema estará disponible en:
   - **Frontend:** `http://localhost:5173`
   - **Backend API:** `http://localhost:8000`
   - **Documentación API (Swagger):** `http://localhost:8000/docs`

## 📊 Portales Integrados

| Portal | URL | Estado |
| :--- | :--- | :--- |
| Finca Raíz | fincaraiz.com.co | ✅ Activo |
| El Castillo | elcastillo.com.co | ✅ Activo |
| Santa Fe | santafe.com | ✅ Activo |
| Panda | pandainmobiliaria.com | ✅ Activo |
| Integridad | integridad.com.co | ✅ Activo |
| Protebienes | protebienes.com.co | ✅ Activo |
| La Castellana | lacastellana.com.co | ✅ Activo |
| Monserrate | monserrate.com | ✅ Activo |
| Aportal | aportal.com.co | ✅ Activo |

## 🏗️ Estructura del Proyecto

- `/backend`: Lógica de scraping, API y modelos de datos.
- `/frontend`: Dashboard interactivo en React.
- `docker-compose.yml`: Orquestación de servicios (DB, Redis, Worker, API, Frontend).

---
Desarrollado con ❤️ para el mercado inmobiliario de Medellín.
