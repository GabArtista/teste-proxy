#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] waiting for database ${POSTGRES_HOST}:${POSTGRES_PORT}"
python - <<'PY'
import os
import time
import psycopg2

host = os.getenv("POSTGRES_HOST", "db")
port = os.getenv("POSTGRES_PORT", "5432")
user = os.getenv("POSTGRES_USER", "analytics")
password = os.getenv("POSTGRES_PASSWORD", "analytics")
database = os.getenv("POSTGRES_DB", "sabores")

for _ in range(30):
    try:
        psycopg2.connect(host=host, port=port, user=user, password=password, dbname=database).close()
        print("[entrypoint] database is ready")
        break
    except Exception as exc:
        print(f"[entrypoint] waiting for db... {exc}")
        time.sleep(2)
else:
    raise SystemExit("database not available")
PY

echo "[entrypoint] running migrations"
python -m app.infrastructure.db.migrate

if [ -n "${DATA_FILE_PATH:-}" ] && [ -f "${DATA_FILE_PATH}" ]; then
  echo "[entrypoint] loading data from ${DATA_FILE_PATH}"
  python -m app.infrastructure.cli.load_data --file "${DATA_FILE_PATH}"
else
  echo "[entrypoint] no data file provided or not found, skipping load"
fi

echo "[entrypoint] starting api"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
