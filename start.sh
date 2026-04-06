# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Criar superuser padrão se não existir (opcional)
# python manage.py createsuperuser --noinput --username=admin --email=admin@example.com 2>/dev/null || true
# Iniciar servidor Django com gunicorn
echo "Iniciando servidor Django..."
exec gunicorn erp_site.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120

#!/bin/bash

echo "=== Django Migration e Deploy ==="

# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Executar migrações do banco de dados
echo "Executando migrações..."
python manage.py migrate --noinput

# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Criar superuser padrão se não existir (opcional)
# python manage.py createsuperuser --noinput --username=admin --email=admin@example.com 2>/dev/null || true

# Criar superuser padrão se não existir (opcional)
# python manage.py createsuperuser --noinput --username=admin --email=admin@example.com 2>/dev/null || true

# Aguardar banco de dados estar pronto (para MySQL)
echo "Aguardando banco de dados..."
sleep 10
# Iniciar servidor Django com gunicorn
echo "Iniciando servidor Django..."
exec gunicorn erp_site.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120