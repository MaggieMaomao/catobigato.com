# CatobiGato — Development Guide

_Last updated: 2026-05-12_

---

## Phase Status

| Phase | Name | Status | Notes |
|-------|------|--------|-------|
| Phase 1 | MVP Core | ✅ Done | FastAPI + auth + DB + calculator |
| Phase 2 | Learning Module | 🔲 Pending | Notes, Questions, Exams |
| Phase 3 | AI + Visualization | 🔲 Pending | VisionSolverAgent, MathAnimator |
| Phase 4 | Puzzles Module | 🔲 Pending | Puzzle bank, crawler infra |
| Phase 5 | Social Features | 🔲 Pending | Follow, groups, messaging |
| Phase 6 | Platform Integrations | 🔲 Pending | Google Calendar, Gmail, WeChat |

---

## Stack Overview

| Layer | Technology | Port |
|-------|-----------|------|
| Frontend | React 19 + Vite + Tailwind CSS v4 | **8081** (dev & prod) |
| Backend API | FastAPI + SQLAlchemy async | **8001** |
| Database | PostgreSQL 17 | 5432 |
| Auth | Keycloak (KeyToMarvel.com) | external |

> **Note**: Port 8000 is occupied by FlowDesk API. Port 8081 is used consistently in both dev and prod to avoid surprises.

---

## Prerequisites

- Python 3.12+
- Node 24+ / Yarn 1.22+
- Docker (for the shared `whereq-postgres:17` container)

### Local PostgreSQL

The shared `whereq-db` Docker container hosts multiple databases. The `catobigato` database was created once with:

```bash
docker exec whereq-db psql -U flowdesk -c "CREATE ROLE catobigato WITH LOGIN PASSWORD '<password>';"
docker exec whereq-db psql -U flowdesk -c "CREATE DATABASE catobigato OWNER catobigato ENCODING 'UTF8';"
docker exec whereq-db psql -U flowdesk -c "GRANT ALL PRIVILEGES ON DATABASE catobigato TO catobigato;"
docker exec whereq-db psql -U flowdesk -d catobigato -c "GRANT ALL ON SCHEMA public TO catobigato;"
```

The password lives in `backend-fastapi/.env` (gitignored). See `.env.example` for required keys.

---

## Local Development

### Backend (FastAPI)

```bash
cd backend-fastapi

# First time setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env: set DB_PASSWORD (and any other values for your local setup)

# Apply database migrations
alembic upgrade head

# Start dev server with hot-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

| URL | Description |
|-----|-------------|
| `http://localhost:8001` | API root |
| `http://localhost:8001/docs` | Swagger UI (interactive API docs) |
| `http://localhost:8001/redoc` | ReDoc API docs |
| `http://localhost:8001/health` | Health check endpoint |

### Frontend (React + Vite)

```bash
cd frontend

# First time setup
yarn install

# Configure environment
cp .env.example .env
# Edit .env: set VITE_KEYCLOAK_URL, VITE_KEYCLOAK_REALM, VITE_KEYCLOAK_CLIENT_ID, VITE_API_BASE_URL

# Start dev server on port 8081
yarn dev
```

Frontend is at `http://localhost:8081`.

The Vite dev server proxies `/api/*` → `http://localhost:8001`, so no CORS configuration is needed during development.

### Running both together (two terminals)

```bash
# Terminal 1 — backend
cd backend-fastapi && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2 — frontend
cd frontend && yarn dev
```

---

## Database Migrations (Alembic)

Alembic is configured for async SQLAlchemy and reads the DB URL from `backend-fastapi/.env`.

```bash
cd backend-fastapi
source venv/bin/activate

# Apply all pending migrations (run this after pulling new code)
alembic upgrade head

# Create a migration after changing a model
alembic revision --autogenerate -m "add_foo_column_to_notes"

# Rollback last migration
alembic downgrade -1

# Show current applied revision
alembic current

# Show full migration history
alembic history --verbose
```

All models are imported in `alembic/env.py` so autogenerate detects schema changes across all six modules: `accounts`, `calculator`, `learning`, `puzzles`, `social`, `visual_math`.

---

## Debugging

### Backend

```bash
# Enable verbose SQL + debug logging
DEBUG=true uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Verify settings are loading from .env
python -c "from app.config import get_settings; s=get_settings(); print(s.database_url, s.keycloak_issuer)"

# Test DB connectivity (replace <password> with value from .env)
python -c "
import asyncio, asyncpg
async def test():
    conn = await asyncpg.connect(host='localhost', port=5432,
                                  user='catobigato', password='<password>',
                                  database='catobigato')
    print(await conn.fetchrow('SELECT current_database(), current_user'))
    await conn.close()
asyncio.run(test())
"

# Check migration state
alembic current

# Preview migration SQL without applying
alembic upgrade head --sql
```

### Frontend

```bash
# Type-check without building
yarn tsc --noEmit

# Full production build (catches all TypeScript errors)
yarn build

# Preview production build on port 8081
yarn preview --port 8081
```

Vite's dev server uses HMR — most changes apply instantly without a page reload. React DevTools work as normal.

### Keycloak auth debugging

If login fails or tokens are rejected:

1. Open **DevTools → Network** and look for requests to `keytomarvel.com`
2. Check `frontend/.env`:
   - `VITE_KEYCLOAK_URL` must be `https://www.keytomarvel.com` — no trailing slash, **no realm path**
   - The Keycloak JS SDK appends the realm path internally
3. In Keycloak admin, confirm the `catobigato` client has **Valid Redirect URIs** including `http://localhost:8081/*`
4. Check backend logs for `401 Invalid token` — the JWT `iss` claim must equal `KEYCLOAK_URL/realms/KEYCLOAK_REALM`
5. Common mistake: `VITE_KEYCLOAK_URL=https://www.keytomarvel.com/realms/catobigato` — this is wrong; the URL should stop at the domain

---

## Project Structure

```
catobigato.com/
├── backend-fastapi/              # FastAPI backend (Python 3.12)
│   ├── app/
│   │   ├── config.py             # Pydantic settings — reads all config from .env
│   │   ├── database.py           # SQLAlchemy async engine + session factory
│   │   ├── dependencies.py       # get_current_user (Keycloak JWT RS256 verification)
│   │   ├── models/               # SQLAlchemy ORM models (one file per domain)
│   │   │   ├── accounts.py       # UserProfile, UserFollow
│   │   │   ├── calculator.py     # CustomFunction, CalculationHistory
│   │   │   ├── learning.py       # Note, Question, QuestionSet, ExamAttempt, StudyGroup
│   │   │   ├── puzzles.py        # PuzzleSource, Puzzle
│   │   │   ├── social.py         # Conversation, Message
│   │   │   └── visual_math.py    # GeoGebraSketch, AnimationProject
│   │   ├── routers/              # FastAPI route handlers (one file per domain)
│   │   │   ├── accounts.py       # /api/v1/accounts/*    ← 7 working endpoints
│   │   │   ├── calculator.py     # /api/v1/calculator/*  ← working (SymPy engine)
│   │   │   ├── learning.py       # /api/v1/learning/*    ← stubs (Phase 2)
│   │   │   ├── puzzles.py        # /api/v1/puzzles/*     ← stubs (Phase 4)
│   │   │   ├── social.py         # /api/v1/social/*      ← stubs (Phase 5)
│   │   │   └── visual_math.py    # /api/v1/visual-math/* ← stubs (Phase 3)
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   └── services/             # Business logic layer
│   │       ├── calculator_engine.py   # SymPy evaluation (6 modes)
│   │       ├── geogebra_service.py    # Rule-based expression → GGBScript
│   │       └── ...                    # Placeholder services (Phase 3+)
│   ├── alembic/                  # Alembic migration environment
│   │   ├── env.py                # Async migration runner (imports all models)
│   │   └── versions/             # Auto-generated migration files
│   ├── alembic.ini               # Alembic config (URL injected from settings)
│   ├── main.py                   # FastAPI app: CORS middleware + router registration
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env                      # Local secrets — gitignored
│   └── .env.example              # Template (no secrets)
│
├── frontend/                     # React 19 + Vite + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx               # Routes, layout, responsive nav, theme/lang controls
│   │   ├── main.tsx              # Keycloak init → ThemeProvider → AuthProvider → React
│   │   ├── auth/
│   │   │   ├── keycloak.ts       # Keycloak-js singleton (URL + realm + clientId only)
│   │   │   └── AuthProvider.tsx  # Context: isAuthenticated, displayName, avatar, login/logout
│   │   ├── theme/
│   │   │   └── ThemeProvider.tsx # Dark/light toggle — localStorage + system pref detection
│   │   ├── api/
│   │   │   └── index.ts          # Axios client with Bearer token interceptor
│   │   ├── i18n/                 # EN / 中文 / FR translation JSON files
│   │   ├── pages/                # Route-level page components
│   │   └── index.css             # Tailwind v4 + CSS variables (light & dark themes)
│   ├── public/
│   │   ├── catobigato.png        # App logo
│   │   ├── favicon.png           # Favicon (copy of catobigato.png)
│   │   └── silent-check-sso.html # Required for Keycloak PKCE silent SSO check
│   ├── index.html                # Entry HTML — title: CatobiGato, favicon: favicon.png
│   ├── vite.config.ts            # Dev port: 8081, /api proxy → :8001
│   ├── .env                      # Local env — gitignored
│   └── .env.example              # Template (no secrets)
│
├── docs/
│   ├── requirements.md           # Product requirements and roadmap
│   ├── SPEC.md                   # Technical spec (pre-alpha reference, partially outdated)
│   ├── DEVELOPMENT.md            # This file
│   └── RUNBOOK.md                # Production deployment guide
├── docker-compose.yml            # Production: catobigato-api:8001 + catobigato-frontend:8081
└── .gitignore
```

---

## API Reference

### Public (no auth)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/calculator/evaluate` | Evaluate math expression (SymPy) |
| POST | `/api/v1/calculator/simplify` | Simplify expression |
| POST | `/api/v1/calculator/factor` | Factor expression |
| POST | `/api/v1/calculator/solve` | Solve equation |
| POST | `/api/v1/calculator/derivative` | Compute derivative |
| POST | `/api/v1/calculator/integrate` | Compute integral |
| POST | `/api/v1/calculator/plot` | Generate plot data |

### Auth-required (Keycloak Bearer token)

| Method | Path | Description |
|--------|------|-------------|
| GET/PUT | `/api/v1/accounts/profile` | Own profile |
| GET | `/api/v1/accounts/profile/{id}` | Any user's public profile |
| POST | `/api/v1/accounts/follow/{id}` | Follow user |
| DELETE | `/api/v1/accounts/follow/{id}` | Unfollow user |
| GET | `/api/v1/accounts/followers` | My followers |
| GET | `/api/v1/accounts/following` | Who I follow |
| GET/POST | `/api/v1/calculator/functions` | List / create custom functions |
| PUT/DELETE | `/api/v1/calculator/functions/{id}` | Update / delete custom function |
| GET | `/api/v1/calculator/history` | Calculation history |

---

## Environment Variables

### `backend-fastapi/.env`

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `DEBUG` | `false` | No | Enable SQLAlchemy query logging |
| `DB_HOST` | `localhost` | No | PostgreSQL host |
| `DB_PORT` | `5432` | No | PostgreSQL port |
| `DB_NAME` | `catobigato` | No | Database name |
| `DB_USER` | `catobigato` | No | Database role |
| `DB_PASSWORD` | — | **Yes** | Database password (no default) |
| `KEYCLOAK_URL` | `https://www.keytomarvel.com` | No | Keycloak base URL |
| `KEYCLOAK_REALM` | `catobigato` | No | Realm name |
| `KEYCLOAK_CLIENT_ID` | `catobigato` | No | Client ID |
| `CORS_ORIGINS` | `["http://localhost:8081"]` | No | Allowed origins (JSON array) |

### `frontend/.env`

| Variable | Description |
|----------|-------------|
| `VITE_KEYCLOAK_URL` | Keycloak base URL — `https://www.keytomarvel.com` |
| `VITE_KEYCLOAK_REALM` | Realm — `catobigato` |
| `VITE_KEYCLOAK_CLIENT_ID` | Client ID — `catobigato` |
| `VITE_API_BASE_URL` | Backend base URL — `http://localhost:8001` |

---

## Key Design Decisions

### Auth: Keycloak-only, no local passwords
- `keycloak_sub` (UUID from Keycloak) is the sole user identity
- JWT RS256 validated against Keycloak's public JWKS endpoint — no shared secret needed
- `UserProfile` is auto-created on first authenticated API call
- Frontend uses PKCE (S256) via `keycloak-js` — Keycloak initialises **before** React mounts

### FastAPI over Django
- Native `async/await` required for Phase 3 LLM pipelines (VisionSolverAgent, MathAnimator)
- Pydantic v2 validation + auto-generated `/docs` (Swagger)
- SQLAlchemy async ORM with `asyncpg` driver

### Theme: CSS variables toggled by `data-theme`
- `[data-theme="dark"]` on `<html>` switches the entire colour palette
- `ThemeProvider` persists choice to `localStorage`, defaults to `prefers-color-scheme`
- All themeable colours use `var(--color-*)` — never Tailwind colour utilities

### Port 8081 everywhere
- Vite dev server and the production Docker container both bind to **8081**
- Avoids conflicts with FlowDesk (8080) and Vite's default 5173
