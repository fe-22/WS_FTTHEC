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
  python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); username='${DJANGO_SUPERUSER_USERNAME}'; email='${DJANGO_SUPERUSER_EMAIL:-admin@example.com}'; password='${DJANGO_SUPERUSER_PASSWORD}'; user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'is_staff': True, 'is_superuser': True}); user.is_staff = True; user.is_superuser = True; user.email = email; (user.set_password(password), user.save()) if created else user.save(); print('Superuser created:' if created else 'Superuser already exists:', username)"
fi

echo "=== Starting Gunicorn ==="
exec gunicorn erp_site.wsgi:application \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers "${GUNICORN_WORKERS:-1}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-180}"
