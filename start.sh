#!/bin/sh
set -e

echo "=== Django start ==="

exec gunicorn erp_site.wsgi:application \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers 1 \
  --threads 1 \
  --timeout 180