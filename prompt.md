# INFRAESTRUCTURA DE DESPLIEGUE (DEDICADA)
- **Servidor:** VPS Hostinger (KVM) Dedicado Exclusivamente al proyecto.
- **Acceso:** Acceso Root completo (posibilidad de formatear e instalar SO desde cero).
- **Especificaciones de Hardware:**
  - CPU: 2 vCores
  - RAM: 8 GB (DDR4/5)
  - Almacenamiento: 100 GB NVMe/SSD
- **Sistema Operativo Base:** Ubuntu 24.04 LTS (o la versión estable más reciente).

# INSTRUCCIONES DE ARQUITECTURA "BARE METAL" vs DOCKER
Aunque tengo acceso total, **seguiremos usando Docker y Docker Compose** como estándar de orquestación.
- **Justificación:** Facilita la recuperación ante desastres y mantiene limpio el sistema base.
- **Ajuste de Recursos:**
  - Configura los contenedores para aprovechar los 8GB de RAM.
  - Base de Datos (PostgreSQL): Asignar `shared_buffers` generosos (ej. 2GB) en la configuración.
  - Scraping Workers (Celery): Dado que tenemos 2 CPUs pero buena RAM, configura la concurrencia de Playwright para ejecutar entre **3 a 4 navegadores simultáneos** (balanceando carga de CPU).

# STACK TECNOLÓGICO SELECCIONADO (Ajustado a 8GB RAM)
1. **Backend & Scraping:** Python 3.12+ con **FastAPI**.
   - **Motor de Scraping:** **Playwright** (Python).
   - *Nota:* Al tener 8GB de RAM, podemos mantener los contextos del navegador abiertos más tiempo para evitar el overhead de arranque, mejorando la velocidad de scraping.
2. **Base de Datos:** **PostgreSQL 16** (con extensión PostGIS opcional para futuras búsquedas por mapa).
   - No necesitamos una base de datos externa ligera (SQLite); el servidor aguanta Postgres completo sin problemas.
3. **Frontend:** **React** + **Vite** (Node.js para build, Nginx para servir estáticos).
   - Nginx actuará como Reverse Proxy manejando SSL (Let's Encrypt) y sirviendo el Front.
4. **Cola de Tareas:** **Redis** (como broker para Celery).
   - Redis puede configurarse para usar persistencia en disco (AOF) dado que tenemos 100GB de espacio, asegurando que no se pierda la cola de scraping si se reinicia el servidor.
5. **Dashboard de Administración:**
   - Opcional: Instalar **Portainer** para gestionar los contenedores visualmente, ya que sobran recursos.

# CRITERIOS DE RENDIMIENTO
- El cuello de botella serán los **2 vCores**. El código de scraping debe ser altamente asíncrono (`asyncio`) para no bloquear el CPU esperando respuestas de red.
- Usar **Playwright Stealth** para minimizar bloqueos sin consumir CPU excesivo en resolución de captchas complejos localmente.

Aquí tienes el prompt definitivo y optimizado para **Antigravyti**.

Este prompt está diseñado estructuralmente para obligar a la IA a trabajar paso a paso (iterativamente), impidiendo que intente generar todo el código de una sola vez y cometa errores. Incorpora las especificaciones exactas de tu hardware (VPS 8GB RAM) y tu desglose de fases.

Copia y pega el siguiente bloque en el editor:

***

# ROL: ARQUITECTO DE SOFTWARE SENIOR Y EXPERTO DEVOPS

Vas a liderar el desarrollo del "Medellín Real Estate Monitor". Tu objetivo es construir una solución robusta, escalable y mantenible para un VPS dedicado.

**⚠️ INSTRUCCIÓN MAESTRA DE COMPORTAMIENTO (CRÍTICO):**
**NO GENERES TODO EL CÓDIGO DE UNA VEZ.**
Vamos a trabajar bajo una metodología estricta de **Desarrollo Iterativo**. Tu tarea es planificar todo, pero **EJECUTAR SOLO UNA FASE A LA VEZ**.
1. Lee este prompt.
2. Genera el plan de arquitectura y los archivos de configuración iniciales.
3. **DETENTE** y espera mi instrucción para comenzar la FASE 1.
4. Cuando yo te diga "Inicia Fase 1", desarrollas solo esa fase.
5. Al terminar una fase, **DETENTE** y espera mi feedback antes de pasar a la siguiente.

***

# 1. INFRAESTRUCTURA (VPS DEDICADO)
El despliegue será en un VPS de Hostinger con acceso root total.
- **Hardware:** 2 vCPU, **8 GB RAM**, 100 GB SSD.
- **OS:** Ubuntu Linux (Latest LTS).
- **Estrategia:** Usaremos **Docker y Docker Compose** para orquestar los servicios, aprovechando los 8GB de RAM para optimizar PostgreSQL y la concurrencia de Playwright.

# 2. STACK TECNOLÓGICO
- **Backend:** Python (FastAPI) + Playwright (Scraping) + Celery (Colas).
- **Base de Datos:** PostgreSQL (Optimizado para 8GB RAM).
- **Frontend:** React + Vite + TailwindCSS.
- **Orquestación:** Docker Compose.

***

# 3. ROADMAP DE EJECUCIÓN (TUS INSTRUCCIONES)

Debes seguir rigurosamente este plan de 7 fases. No adelantes funcionalidades de fases futuras.

### FASE 1: MVP - SCRAPING SINGLE-SITE (Foco Actual)
**Objetivo:** Validar la infraestructura y el motor de scraping con UN solo sitio (ej. fincaraiz.com.co).
- Configurar `docker-compose.yml` (Postgres + Redis + Backend básico).
- Crear script de Playwright que extraiga: Título, Precio, Ubicación, Link.
- Guardar datos en PostgreSQL.
- **Validación:** El script corre diariamente y detecta *nuevos* items vs los de ayer.

### FASE 2: SCRAPING AVANZADO Y MULTI-SITIO
**Objetivo:** Escalar la lógica para múltiples portales y monitoreo profundo.
- Abstraer la lógica de scraping (Patrón Strategy) para soportar múltiples sitios (ciencuadras, etc.).
- Implementar lógica de "Diff": Detectar cambios de precio y propiedades eliminadas.
- Manejo de rotación de User-Agents y retardos inteligentes.

### FASE 3: INTERFAZ DE USUARIO INICIAL (DASHBOARD)
**Objetivo:** Visualización básica.
- Setup del proyecto React.
- Crear endpoint API `GET /properties`.
- Vista de Tabla/Lista con los inmuebles recolectados.

### FASE 4: CONFIGURACIÓN Y FILTROS
**Objetivo:** Panel de control.
- Frontend: Inputs para configurar URLs, rangos de precios, barrios.
- Backend: Endpoints para guardar esta configuración en DB.
- Filtrado dinámico en la API.

### FASE 5: INTEGRACIÓN DE ACCIONES (WHATSAPP)
**Objetivo:** Operatividad.
- Botón "Contactar" que genera enlace `wa.me` con mensaje pre-llenado.
- Detalles completos del inmueble (modal o página dedicada).

### FASE 6: ANALÍTICA
**Objetivo:** Inteligencia de mercado.
- Calcular estadísticas: Precio/m² promedio por barrio.
- Gráficos de tendencias (Librería: Recharts o Chart.js).

### FASE 7: EXPORTACIÓN Y ENTREGA FINAL
**Objetivo:** Salida de datos.
- Generación de CSV/Excel desde el backend.
- Documentación final de despliegue y mantenimiento.

***

# 4. ESPECIFICACIONES FUNCIONALES DETALLADAS
*(Referencia para todo el desarrollo)*

**A. CRITERIOS DE FILTRADO:**
- Ubicación: Medellín (Barrios específicos).
- Tipo: Vivienda > 40m².
- Filtrado por precio configurable.

**B. FUNCIONALIDADES CORE:**
- Scraping a las 6:00 AM (Cron/Celery Beat).
- Historial de precios obligatorio.
- Identificación de "Nuevo", "Bajó de precio", "Vendido".

***

# ACCIÓN INICIAL REQUERIDA
Para comenzar, por favor:
1. **Confirma que entiendes que trabajaremos fase por fase.**
2. Genera la estructura de carpetas del proyecto (`tree`).
3. Genera el archivo `docker-compose.yml` base optimizado para mis 8GB de RAM.
4. Genera el documento `PLAN_DE_TRABAJO.md` resumiendo las fases.

**NO ESCRIBAS CÓDIGO DE SCRAPING NI DE REACT TODAVÍA. ESPERA MI ORDEN PARA LA FASE 1.**

# PREGUNTA SOBRE FLUJO DE TRABAJO (RESPONDER ANTES DE EMPEZAR)
Tengo una duda crítica sobre el entorno de desarrollo que necesito que resuelvas en tu primera respuesta:
¿Cuál es la estrategia óptima para desarrollar y probar este proyecto?
- Mi PC local es **Windows**.
- Mi servidor de producción es el **VPS Linux (Ubuntu)**.
- Tú (Antigravyti) estás en la nube.

Por favor, recomiéndame el flujo de trabajo: ¿Debo conectar Antigravyti directamente vía SSH al VPS para desarrollar ahí ("Remote Development")? ¿O debo desarrollar localmente en mi Windows con Docker Desktop y luego hacer deploy al VPS?
Dada la naturaleza del scraping (necesidad de probar selectores en tiempo real) y mi hardware local, dime cuál es la opción con menos fricción.
