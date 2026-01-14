# Medellín Real Estate Monitor - Definitive Project Context

## 1. Project Identity & Purpose
**Project Name:** Medellín Real Estate Monitor (WebScrapingInmobiliaria)
**Author:** MarlonMedellin / Antigravyti
**Goal:** Create a robust, scalable real estate monitoring system for Medellín, specifically tracking **rental market (Arriendos)** opportunities.
**Repository:** [https://github.com/MarlonMedellin/WebScrapingInmobiliaria](https://github.com/MarlonMedellin/WebScrapingInmobiliaria)
**Production Domain:** `csimedellin.link` (VPS Hostinger)

---

## 2. Infrastructure & Constraints
This project is designed for a **dedicated VPS** with specific hardware constraints that shaped the architecture.

*   **Environment:** Production VPS (Ubuntu 24.04 LTS), Development (Windows/Docker).
*   **Hardware:** 2 vCPU, **8 GB RAM**, 100 GB NVMe.
*   **Orquestration:** **Docker & Docker Compose** (Strict requirement).
*   **Optimization:**
    *   **PostgreSQL:** Tuned for 8GB RAM (`shared_buffers` generous).
    *   **Playwright:** 3-4 concurrent browsers max (limited by 2 vCPUs).
    *   **Architecture:** Fully asynchronous (FastAPI + Celery) to avoid blocking the limited CPU.

---

## 3. Technology Stack

### Backend (`/backend`)
*   **Language:** Python 3.12+
*   **Framework:** **FastAPI** (API REST for frontend and control).
*   **Scraping Engine:** **Playwright** (Python) + **BeautifulSoup4**.
*   **Task Queue:** **Celery** + **Redis** (Broker & Result Backend).
*   **Database:** **PostgreSQL 16** (SQLAlchemy ORM).
*   **Key Patterns:**
    *   **Strategy Pattern:** [`BaseScraper`](backend/scrapers/base.py) handles common logic (browser, DB, errors).
    *   **Factory Pattern:** [`ScraperFactory`](backend/scrapers/factory.py) dynamically instantiates scrapers.

### Frontend (`/frontend`)
*   **Framework:** **React** + **Vite**.
*   **Styling:** Custom CSS (Glassmorphism, Dark Mode).
*   **Deployment:** Nginx (Reverse Proxy) + SSL via Cloudflare.

---

## 4. Project Structure (Map for AI)

```text
/WebScrapingInmobiliaria
├── .gitignore
├── docker-compose.yml       # Orchestration (db, redis, backend, worker, frontend)
├── README.md                # Public documentation
├── docs/                    # Detailed technical documentation
│   ├── PROJECT_CONTEXT.md   # This file (Context, Architecture, Roadmap)
│   ├── LOCAL_DEV_GUIDE.md   # Setup, workflows, scripts
│   ├── SCRAPING_GOLDEN_RULES.md # Rules and Portal Directory
│   └── CHANGELOG_AND_FIXES.md # Fix logs and history
├── backend/                 # Python/FastAPI Application
│   ├── main.py              # API Endpoints
│   ├── models.py            # SQLAlchemy Model
│   ├── tasks.py             # Celery Tasks
│   ├── scrapers/            # Scraping Logic
│   │   ├── base.py
│   │   ├── factory.py
│   │   ├── config.py
│   │   └── ... (portals)
│
└── frontend/                # React Application
    ├── src/
    │   ├── App.jsx          # Dashboard Main View
    │   └── ...
```

---

## 5. Architecture Deep Dive

### Microservices Overview
1.  **Frontend (React + Vite):** SPA Dashboard for visualization, filtering, and manual task triggering.
2.  **API (FastAPI):** Entry point for frontend, DB management, and task queuing.
3.  **Worker (Celery):** Background processing engine running scrapers via **Playwright**.
4.  **Database (PostgreSQL 16):** Persistence of properties, states, and saved searches.
5.  **Broker (Redis):** Message queue for Celery and temporary cache.
6.  **Proxy (Nginx):** Reverse proxy for production, handling traffic to frontend and backend.

### Intelligent Scraping System
#### 1. BaseScraper
All scrapers inherit from `backend/scrapers/base.py`, standardizing:
- **Playwright Initialization:** User-Agents, Headless mode.
- **Robust Navigation:** Timeout handling.
- **Property Processing:** Logic to determine if a property is NEW, UPDATED, or EXISTING.
- **Stop Mechanism:** Stops after $N$ consecutive existing records to save resources.

#### 2. High-Precision Curated Mapping
- **Broad Collection:** Scrapes everything in the target area to avoid missing data.
- **Manual Mapping (`neighborhood_map.json`):** Curated master file with 200+ variants mapped to standard neighborhoods.
- **DB Normalization:** Properties get a `neighborhood_resolved` field used for strict filtering in the Dashboard.

### Data Model (`Property`)
- **Core Fields:** Title, Price, Location, Link, Image, Source, Area, Bedrooms, Bathrooms.
- **States:** `NEW`, `SEEN`, `ARCHIVED`, `FAVORITE`.
- **Fields:** `portal_published_date` (for freshness tracking), `last_seen` (for auto-archival).

---

## 6. Comprehensive Roadmap & Status (Jan 2026)

**Overall Progress:** ~95% (Approaching Production Readiness)

### ✅ Completed Milestones
*   **Infrastructure:** Stable Docker environment (Dev & Prod parity).
*   **Phase 1-2 (Scraping):** 17 Portals integrated (Fincaraiz, El Castillo, Santa Fe, Panda, etc.).
*   **Phase 3-4 (UI/UX):** Dashboard with stats grid, manual triggers, and advanced filtering.
*   **Phase 5 (Actions):** WhatsApp integration, Detail Modal.
*   **Phase 6 (Optimization):** Strict pre-save filtering, Early Stopping, Freshness Badges.
*   **Phase 10 (Production):** VPS Deployment, Nginx Gateway, Cloudflare SSL.

### ⏳ Future Strategy
#### Phase 7: Analytics
- Price/m² calculations per zone.
- Trend charts (Recharts/Chart.js).

#### Phase 8: Notifications
- Telegram Bot integration.
- Email alerts for new listings.

#### Phase 9: Export & API
- Excel/CSV export.
- Public API for third parties.

---

## 7. Future Portals Strategy (Candidates)

| Portal | Status | Notes |
| :--- | :--- | :--- |
| **Inmobiliaria Conquistadores** | ✅ | Implemented. |
| **Arrendamientos del Norte** | ⏳ | Pending investigation (North Zone/Bello). |
| **Acierto Inmobiliario** | ⏳ | Pending investigation. |
| **Inmobiliaria Medellín (Real)**| ⏳ | Pending investigation (inmobiliariamedellin.com). |
| **Gómez y Asociados** | ⏳ | Pending investigation. |
| **Arrendamientos Envigado** | ⏳ | Pending investigation. |
| **Santamaría Propiedad Raíz**| ⏳ | Pending investigation. |

**Integration Protocol:**
1.  Verify "Golden URL" and selectors.
2.  Create `backend/scrapers/new_portal.py`.
3.  Register in `factory.py` and `App.jsx`.
