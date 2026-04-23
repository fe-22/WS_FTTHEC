#!/bin/bash
# setup.sh - Script de configuração do projeto ERP Site

echo "🚀 Configurando o projeto ERP Site..."

# Criar ambiente virtual
echo "1. Criando ambiente virtual..."
python -m venv venv

# Ativar ambiente virtual
echo "2. Ativando ambiente virtual..."
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependências
echo "3. Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Configurar variáveis de ambiente
echo "4. Configurando variáveis de ambiente..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  ATENÇÃO: Edite o arquivo .env com suas configurações!"
fi

# Executar migrações
echo "5. Executando migrações..."
python manage.py migrate

# Coletar arquivos estáticos
echo "6. Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Criar superusuário (opcional)
echo "7. Criar superusuário? (s/n)"
read criar_su
if [[ "$criar_su" == "s" ]]; then
    python manage.py createsuperuser
fi

echo "✅ Configuração concluída!"
echo ""
echo "📋 Para iniciar o servidor:"
echo "   source venv/bin/activate  # Ativar ambiente"
echo "   python manage.py runserver"
echo ""
echo "🌐 Acesse: http://localhost:8000"