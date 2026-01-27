# app.py - VERSÃO CORRIGIDA
import os
import sys
from django.core.wsgi import get_wsgi_application

# Configura o Django CORRETAMENTE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_site.settings')

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Cria a aplicação
application = get_wsgi_application()

# Para o gunicorn
app = application