#!/bin/bash
# start.sh
echo "=== Iniciando Django no Render ==="
echo "Diretório atual: $(pwd)"
echo "Arquivos:"
ls -la

echo "Python path:"
python -c "import sys; print('\n'.join(sys.path))"

echo "Testando import do Django..."
python -c "import django; print('Django version:', django.get_version())"

echo "Testando app.py..."
python -c "from app import app; print('App importado com sucesso!')"

echo "Iniciando gunicorn..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --access-logfile - --error-logfile -