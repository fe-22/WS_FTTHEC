#!/bin/sh
set -e

echo "=== Django startup ==="

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  echo "=== Running migrations ==="
  python manage.py migrate --noinput
fi

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "=== Ensuring Django superuser ==="
  python manage.py reset_crm_password "$DJANGO_SUPERUSER_USERNAME" \
    --create \
    --staff \
    --superuser \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" \
    --password "$DJANGO_SUPERUSER_PASSWORD" \
    --no-crm-request \
    --hide-password
fi

echo "=== Starting Gunicorn ==="
exec gunicorn erp_site.wsgi:application \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers "${GUNICORN_WORKERS:-1}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-180}"
