# CatobiGato — Operations Runbook

## Production Status

**Deployed on**: RP4 (whereq@rp4)
**Cloudflare Tunnel**: catobigato.com → RP4 host → nginx on 8081

```
catobigato.com/*  →  RP4:8081  (nginx routes /api → catobigato-api:8001)
```

---

## Quick Reference

| Service | Container | Host Port | Status |
|---|---|---|---|
| `catobigato-api` | FastAPI (uvicorn) | `8001` | running |
| `catobigato-frontend` | Nginx (SPA) | `8081` | running |
| `whereq-db` | PostgreSQL 17 | `5432` | existing |
| `keycloak-k2m` | Keycloak | `8888` | existing |

**Public endpoints**:
- Frontend: https://catobigato.com
- API: https://catobigato.com/api
- Swagger docs: https://catobigato.com/docs

---

## 1. Deploy / Restart

```bash
cd /home/whereq/github/catobigato.com

# Full rebuild + restart
docker compose build && docker compose up -d

# Restart without rebuild
docker compose restart

# View logs
docker logs -f catobigato-api
docker logs -f catobigato-frontend
```

---

## 2. Container Details

### catobigato-api
- **Image**: `catobigatocom-catobigato-api` (local)
- **Internal port**: `8001` / **Host port**: `8001`
- **Env** (set via `.env.production` at `backend-fastapi/`):
  - `DB_HOST=whereq-db`, `DB_PORT=5432`, `DB_NAME=catobigato`
  - `DB_USER=catobigato`, `DB_PASSWORD=CatoBigato2026!`
  - `KEYCLOAK_URL=https://www.keytomarvel.com`
  - `KEYCLOAK_REALM=catobigato`, `KEYCLOAK_CLIENT_ID=catobigato`
  - `CORS_ORIGINS=["https://catobigato.com","http://catobigato.com"]`
- **API docs**: `https://catobigato.com/docs`

### catobigato-frontend
- **Image**: `catobigatocom-catobigato-frontend` (local)
- **Internal port**: `80` / **Host port**: `8081`
- **Proxies**: `/api/*` → `catobigato-api:8001` (Docker DNS)
- **SPA fallback**: All non-API routes → `index.html`

---

## 3. Docker Compose File

Location: `/home/whereq/github/catobigato.com/docker-compose.yml`

```yaml
services:
  catobigato-api:
    build: ./backend-fastapi
    container_name: catobigato-api
    restart: unless-stopped
    environment:
      - DB_HOST=whereq-db
      - DB_NAME=catobigato
      - DB_USER=catobigato
      - DB_PASSWORD=${DB_PASSWORD:-CatoBigato2026!}
      - KEYCLOAK_URL=https://www.keytomarvel.com
      - KEYCLOAK_REALM=catobigato
      - KEYCLOAK_CLIENT_ID=catobigato
      - CORS_ORIGINS=["https://catobigato.com","http://catobigato.com"]
    ports:
      - "8001:8001"

  catobigato-frontend:
    build: ./frontend
    container_name: catobigato-frontend
    restart: unless-stopped
    ports:
      - "8081:8081"
    depends_on:
      - catobigato-api
```

### External services (already running — NOT managed here)
- `whereq-db` (PostgreSQL) — port 5432
- `keycloak-k2m` — port 8888

---

## 4. Cloudflare Tunnel

Cloudflare tunnel routes `catobigato.com` to RP4 host on port 8081. No container changes needed.

```
catobigato.com/*  →  RP4:8081  (nginx inside container)
                        nginx proxies /api/* → catobigato-api:8001
```

---

## 5. Database

- **Database**: `catobigato` (already exists in `whereq-db`)
- **Role**: `catobigato` / `CatoBigato2026!`
- **Connection string**: `postgresql://catobigato:CatoBigato2026!@whereq-db:5432/catobigato`
- **pgpass (RP4 local)**: `localhost:5432:catobigato:catobigato:CatoBigato2026!`

---

## 6. Keycloak

- **URL**: `https://www.keytomarvel.com`
- **Realm**: `catobigato`
- **Client**: `catobigato`
- **Valid Redirect URIs**: `https://catobigato.com/*`

---

## 7. Environment Files

| File | Used by | Contents |
|---|---|---|
| `backend-fastapi/.env` | Local dev (`uvicorn` direct) | Dev settings |
| `backend-fastapi/.env.production` | Docker container | Prod settings |
| `frontend/.env` | Local dev (`yarn dev`) | Dev API URL |
| `frontend/.env.production` | `yarn build` (baked into image) | Prod API URL |

---

## 8. Troubleshooting

### API 401 — Keycloak token validation failed
```bash
docker exec catobigato-api curl -s https://www.keytomarvel.com/realms/catobigato/.well-known/openid-configuration | head -5
```

### Frontend blank page
- Check browser console for CORS or 404 errors
- Verify `VITE_API_BASE_URL` matches deployed domain

### Database connection refused
```bash
docker exec catobigato-api nc -zv whereq-db 5432
```

### Container won't start
```bash
docker logs catobigato-api
docker logs catobigato-frontend
```

---

## 9. Local Dev vs Production

| | Local Dev | Production |
|---|---|---|
| Frontend | `yarn dev` :5173 | Nginx container :8081 |
| API | `uvicorn` :8001 | Docker container :8001 |
| DB | whereq-db:5432 | Same |
| Keycloak | keytomarvel.com | Same |
| CORS | localhost:5173 | https://catobigato.com |

---

## 10. Project File Structure

```
/home/whereq/github/catobigato.com/
├── docker-compose.yml              # Production orchestration
├── backend-fastapi/
│   ├── Dockerfile                  # Python 3.12-slim + uvicorn
│   ├── requirements.txt
│   ├── .env                        # Dev
│   ├── .env.production             # Prod (loaded by container)
│   └── app/
│       ├── main.py                # FastAPI entry
│       ├── config.py              # pydantic-settings
│       ├── database.py            # SQLAlchemy async (asyncpg)
│       ├── dependencies.py        # Keycloak JWT auth
│       ├── models/                # SQLAlchemy → existing Django tables
│       │   ├── accounts.py        # UserProfile, UserFollow
│       │   ├── calculator.py     # CustomFunction, CalculationHistory
│       │   ├── learning.py        # Note, Question, QuestionSet, etc.
│       │   ├── puzzles.py         # PuzzleSource, Puzzle
│       │   ├── social.py          # Conversation, Message
│       │   └── visual_math.py     # GeoGebraSketch, AnimationProject
│       ├── routers/               # API route handlers
│       │   ├── accounts.py        # Profile, follow/unfollow
│       │   └── calculator.py      # Evaluate, functions, history
│       └── services/
│           └── calculator_engine.py  # SymPy engine
└── frontend/
    ├── Dockerfile                  # Node → nginx multi-stage
    ├── nginx.frontend.conf         # SPA + /api proxy config
    ├── vite.config.ts             # Vite + TailwindCSS 4
    ├── .env                        # Dev
    ├── .env.production            # Prod (baked into build)
    └── src/
        ├── App.tsx                # Router + Nav
        ├── api/index.ts           # Axios client
        ├── auth/keycloak.ts       # keycloak-js singleton
        ├── hooks/useAuth.ts       # useAuth hook
        ├── i18n/                  # EN, ZH, FR translations
        └── pages/                  # CalculatorPage, HomePage, etc.
```