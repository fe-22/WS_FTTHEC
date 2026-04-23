#!/bin/sh
set -e

echo "=== Iniciando aplicacao Django ==="

python manage.py collectstatic --noinput
python manage.py migrate --noinput

HOST="${GUNICORN_HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${GUNICORN_WORKERS:-2}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"

echo "Subindo Gunicorn em ${HOST}:${PORT} com ${WORKERS} workers"
exec gunicorn erp_site.wsgi:application \
    --bind "${HOST}:${PORT}" \
    --workers "${WORKERS}" \
    --timeout "${TIMEOUT}"
