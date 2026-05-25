# CatobiGato — Production Runbook

_Last updated: 2026-05-12_

---

## Production Overview

| Item | Detail |
|------|--------|
| Server | Raspberry Pi 4 (`whereq@rp4`) |
| Repo path | `/home/whereq/github/catobigato.com` |
| Public URL | https://catobigato.com |
| Routing | Cloudflare Tunnel → RP4:8081 (nginx) → /api → catobigato-api:8001 |

### Running containers

| Container | Role | Host Port |
|-----------|------|-----------|
| `catobigato-api` | FastAPI + uvicorn | 8001 |
| `catobigato-frontend` | Nginx SPA + /api proxy | 8081 |
| `whereq-db` | PostgreSQL 17 (shared, pre-existing) | 5432 |
| `keycloak-k2m` | Keycloak (shared, pre-existing) | 8888 |

**Public endpoints:**
- Frontend: https://catobigato.com
- API: https://catobigato.com/api/v1
- Swagger docs: https://catobigato.com/docs

---

## Deployment

### Prerequisites (one-time, already done)
- `whereq-db` PostgreSQL container running with `catobigato` database and role
- `catobigato-api` and `catobigato-frontend` on a Docker network that can reach `whereq-db`
- Keycloak realm `catobigato` configured with redirect URI `https://catobigato.com/*`

---

### Standard deploy (code update)

```bash
ssh whereq@rp4
cd /home/whereq/github/catobigato.com

git pull

docker compose build
docker compose up -d
```

The `catobigato-api` container runs `entrypoint.sh` on startup, which:
1. Waits up to 30 s for PostgreSQL to be ready
2. Detects whether Alembic has been initialised (checks for `alembic_version` table)
3. If first deploy after Alembic was added: stamps the DB at the current revision (no destructive changes)
4. Runs `alembic upgrade head` (applies any new migrations)
5. Starts `uvicorn`

No manual migration steps are needed for a standard deploy.

---

### First deploy — IMPORTANT (existing DB without Alembic)

> **This applies only once**: the very first time deploying after Alembic was added to the project.
> The PROD database already has all tables from the previous deployment but has no `alembic_version` table.
> The entrypoint script handles this automatically — no manual steps required.
>
> The script detects the missing `alembic_version` table and runs `alembic stamp head` before
> `alembic upgrade head`, which registers the existing schema without touching any data or tables.

If you want to verify the stamp happened correctly after the first deploy:

```bash
docker exec whereq-db psql -U catobigato -d catobigato -c "SELECT * FROM alembic_version;"
```

You should see one row with the revision ID of the initial migration.

---

### Rolling back a migration

```bash
# Roll back one migration
docker exec catobigato-api alembic downgrade -1

# Roll back to a specific revision
docker exec catobigato-api alembic downgrade <revision_id>

# Then restart the API
docker compose restart catobigato-api
```

---

### Force-rebuild without cache

```bash
docker compose build --no-cache
docker compose up -d
```

---

## Quick-reference commands

```bash
# Restart all services (no rebuild)
docker compose restart

# Restart only the API
docker compose restart catobigato-api

# Restart only the frontend
docker compose restart catobigato-frontend

# View live API logs
docker logs -f catobigato-api

# View live frontend logs
docker logs -f catobigato-frontend

# Check migration state
docker exec catobigato-api alembic current

# Open a DB shell
docker exec -it whereq-db psql -U catobigato -d catobigato

# Check running containers
docker compose ps

# build/run front-end
docker compose build catobigato-frontend
docker compose up -d catobigato-frontend
```

---

## Configuration

### docker-compose.yml environment

The API container reads all config from environment variables injected by `docker-compose.yml`.
No `.env.production` file is needed on the server — docker-compose handles it.

Key variables (see `docker-compose.yml`):

| Variable | Production value |
|----------|-----------------|
| `DB_HOST` | `whereq-db` |
| `DB_NAME` | `catobigato` |
| `DB_USER` | `catobigato` |
| `DB_PASSWORD` | Set via `${DB_PASSWORD}` host env or compose default |
| `KEYCLOAK_URL` | `https://www.keytomarvel.com` |
| `CORS_ORIGINS` | `["https://catobigato.com","http://catobigato.com"]` |

To override the DB password securely without editing docker-compose.yml:

```bash
# On RP4, set the env var before running compose
export DB_PASSWORD="your_actual_password"
docker compose up -d
```

### Frontend production build

The frontend Docker build bakes env vars in at build time via ARGs (defaults set in `frontend/Dockerfile`):

| ARG | Default |
|-----|---------|
| `VITE_KEYCLOAK_URL` | `https://www.keytomarvel.com` |
| `VITE_KEYCLOAK_REALM` | `catobigato` |
| `VITE_KEYCLOAK_CLIENT_ID` | `catobigato` |
| `VITE_API_BASE_URL` | `https://catobigato.com` |

These defaults are correct for production. No `.env.production` file is needed on the server.

---

## Cloudflare Tunnel

Cloudflare Tunnel routes `catobigato.com/*` → RP4 host port 8081.
Nginx inside `catobigato-frontend` then proxies `/api/*` → `catobigato-api:8001`.

No changes to Cloudflare are needed for standard deploys.

---

## Troubleshooting

### API container fails to start

```bash
docker logs catobigato-api
```

Common causes:
- Database unreachable: entrypoint will log `DB not ready (attempt N/30)`
  → check `whereq-db` is running: `docker ps | grep whereq-db`
  → check network: `docker exec catobigato-api nc -zv whereq-db 5432`
- Migration failed: check logs for `alembic` errors
- Import error: Python syntax/import issue in app code

### 401 Unauthorized — token validation fails

```bash
# Verify Keycloak is reachable from the container
docker exec catobigato-api curl -sf https://www.keytomarvel.com/realms/catobigato/.well-known/openid-configuration | python3 -m json.tool | head -10
```

If Keycloak is unreachable, check outbound HTTPS from RP4.

### Frontend shows blank page or API 404

```bash
# Check nginx config and logs
docker exec catobigato-frontend nginx -t
docker logs catobigato-frontend
```

Common causes:
- `/api/` proxy target wrong — must resolve `catobigato-api` by container name
- SPA fallback not working — all non-asset routes must return `index.html`

### Database connection refused

```bash
# From host
docker exec whereq-db pg_isready -U catobigato -d catobigato

# From API container
docker exec catobigato-api python -c "
import asyncio, asyncpg, os
async def t():
    c = await asyncpg.connect(host='whereq-db', port=5432,
        user='catobigato', password=os.getenv('DB_PASSWORD'), database='catobigato')
    print(await c.fetchrow('SELECT version()'))
    await c.close()
asyncio.run(t())
"
```

---

## Local Dev vs Production

| | Local Dev | Production |
|--|-----------|-----------|
| Frontend URL | http://localhost:8081 | https://catobigato.com |
| API URL | http://localhost:8001 | https://catobigato.com/api/v1 |
| Frontend port | 8081 (Vite dev server) | 8081 (nginx container) |
| API serving | uvicorn direct (hot-reload) | uvicorn in Docker |
| DB host | `localhost` (Docker port 5432) | `whereq-db` (Docker DNS) |
| CORS origins | `http://localhost:8081` | `https://catobigato.com` |
| Migrations | `alembic upgrade head` (manual) | Automatic via `entrypoint.sh` |
| Frontend env | `frontend/.env` | Baked into Docker image via ARGs |
