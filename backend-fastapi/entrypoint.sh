#!/bin/bash
# CatobiGato API entrypoint
# 1. Wait for PostgreSQL to be ready
# 2. Stamp Alembic revision if this is the first deploy (tables exist, no alembic_version)
# 3. Run any pending migrations
# 4. Start the API server

set -e

echo "[startup] Waiting for database..."

python - <<'PYEOF'
import asyncio, asyncpg, os, sys

async def main():
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5432"))
    name = os.getenv("DB_NAME", "catobigato")
    user = os.getenv("DB_USER", "catobigato")
    pwd  = os.getenv("DB_PASSWORD", "")

    for attempt in range(1, 31):
        try:
            conn = await asyncpg.connect(
                host=host, port=port, database=name, user=user, password=pwd
            )
            has_alembic = await conn.fetchval(
                "SELECT EXISTS("
                "  SELECT 1 FROM information_schema.tables"
                "  WHERE table_schema='public' AND table_name='alembic_version'"
                ")"
            )
            await conn.close()
            print(f"[startup] Database ready. alembic_version exists: {has_alembic}")
            sys.exit(0 if has_alembic else 1)
        except Exception as e:
            print(f"[startup] DB not ready (attempt {attempt}/30): {e}")
            await asyncio.sleep(1)

    print("[startup] ERROR: database never became ready")
    sys.exit(2)

asyncio.run(main())
PYEOF

EXIT_CODE=$?

if [ "$EXIT_CODE" -eq 2 ]; then
    echo "[startup] Fatal: cannot connect to database. Aborting."
    exit 1
elif [ "$EXIT_CODE" -eq 1 ]; then
    echo "[startup] First deploy detected — stamping existing database at current revision..."
    alembic stamp head
    echo "[startup] Stamp complete."
fi

echo "[startup] Running database migrations..."
alembic upgrade head
echo "[startup] Migrations complete."

echo "[startup] Starting API server on :8001"
exec uvicorn main:app --host 0.0.0.0 --port 8001
