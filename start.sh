#!/bin/bash
set -e

echo "=== Iniciando aplicacao ==="

# Aguardar banco de dados estar pronto
echo "Aguardando banco de dados..."
sleep 10

echo "Rodando migrations..."
python manage.py migrate --noinput

echo "Iniciando servidor Gunicorn..."
exec gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 120 erp_site.wsgi:application
