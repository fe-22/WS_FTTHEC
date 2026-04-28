import os
from pathlib import Path
from dotenv import load_dotenv

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

load_dotenv(override=False)

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


# 🔐 Segurança
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-dev-fallback-key-change-in-production-12345!@#",
)

DEBUG = env_bool("DEBUG", False)
RUNNING_ON_CLOUD_RUN = bool(os.getenv("K_SERVICE"))

APP_ENV = os.getenv(
    "APP_ENV",
    "production" if (RUNNING_ON_CLOUD_RUN or not DEBUG) else "development",
).strip().lower()

IS_DEVELOPMENT = APP_ENV in {"development", "dev", "local"}


# 🔥 CLOUD RUN FIXES
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
if RUNNING_ON_CLOUD_RUN:
    ALLOWED_HOSTS.extend([".run.app", "run.app"])
if IS_DEVELOPMENT:
    for host in ("localhost", "127.0.0.1"):
        if host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))

CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
if RUNNING_ON_CLOUD_RUN:
    CSRF_TRUSTED_ORIGINS.append("https://*.run.app")
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = env_bool("USE_X_FORWARDED_HOST", RUNNING_ON_CLOUD_RUN)

if IS_DEVELOPMENT:
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
else:
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
    CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", True)
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)


# 🌐 CORS
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", False)


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "core",
    "ai_chat",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "erp_site.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "erp_site.wsgi.application"


# 🗄️ BANCO (CORRIGIDO)
database_url = os.getenv("DATABASE_URL", "").strip()

if database_url:
    if dj_database_url is None:
        raise RuntimeError(
            "DATABASE_URL definido, mas dj-database-url não instalado"
        )
    DATABASES = {
        "default": dj_database_url.parse(database_url)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# 🔑 Senhas
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# 🌎 Localização
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True


# 📁 Static
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# 🤖 API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


# 🔐 Sessão
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = int(os.getenv("SESSION_COOKIE_AGE", "3600"))


# 📧 Email
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "fthec@fthec.com.br")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "fthec@fthec.com.br")


# 🔐 Login
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/crm/"
LOGOUT_REDIRECT_URL = "/"
