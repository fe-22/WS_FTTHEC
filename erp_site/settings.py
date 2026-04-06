import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# 'or' garante que string vazia também cai no fallback
SECRET_KEY = os.environ.get("SECRET_KEY") or "django-insecure-dev-fallback-key-change-in-production-12345!@#"

DEBUG = True
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

ALLOWED_HOSTS = ['*']



CSRF_TRUSTED_ORIGINS = [
    "https://erp-django-app-811970467107.southamerica-east1.run.app"
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'core',
    'ai_chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'erp_site.urls'

# CORREÇÃO DOS TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'erp_site.wsgi.application'

# Configuração de banco de dados
# Cloud Run usa Cloud SQL Auth Proxy via Unix socket (CLOUD_SQL_CONNECTION_NAME)
# Dev local usa SQLite
_CLOUD_SQL_CONNECTION_NAME = os.getenv('CLOUD_SQL_CONNECTION_NAME', '')
_DB_HOST = os.getenv('DB_HOST', '')

if _CLOUD_SQL_CONNECTION_NAME:
    # Cloud Run + Cloud SQL Auth Proxy (unix socket — método recomendado pelo Google)
    import pymysql
    pymysql.install_as_MySQLdb()

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'erp_fthec'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': f'/cloudsql/{_CLOUD_SQL_CONNECTION_NAME}',
            'PORT': '',  # Não usar porta com socket
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
elif _DB_HOST:
    # Conexão TCP direta (fallback / testes)
    import pymysql
    pymysql.install_as_MySQLdb()

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'erp_fthec'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': _DB_HOST,
            'PORT': '3306',
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    # SQLite para desenvolvimento local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuração OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Configurações de sessão para o chatbot
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hora

# Configuração de email via .env (use SMTP para envio real)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() in ['true', '1', 'yes']
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', 10))
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'fthec@fthec.com.br')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'fthec@fthec.com.br')

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/crm/'
LOGOUT_REDIRECT_URL = '/'

# CORS Configuration - Permitir requisições de qualquer origem (necessário para o chatbot no Google Cloud)
CORS_ALLOWED_ORIGINS = [
    "https://erp-django-app-811970467107.southamerica-east1.run.app",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]