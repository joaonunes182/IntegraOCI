"""
Configurações Django do IntegraOCI — aplicação standalone.

Variáveis de ambiente carregadas via python-decouple (.env).
"""

from pathlib import Path
from decouple import Csv, config
from datetime import timedelta
from corsheaders.defaults import default_headers
import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Segurança
# ---------------------------------------------------------------------------

SECRET_KEY = config("SECRET_KEY", default="django-insecure-integra-oci-change-in-production")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

# ---------------------------------------------------------------------------
# Aplicações
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    # Django contrib
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceiros
    "corsheaders",
    "ninja",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    # Módulos do IntegraOCI
    "core",
    "BpaApac",
]

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "core.middleware.ForceCSRFMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "core.wsgi.application"

# ---------------------------------------------------------------------------
# Banco de dados principal (auth + módulo BpaApac)
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": config("DB_NAME", default=str(BASE_DIR / "db.sqlite3")),
        "USER": config("DB_USER", default=""),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default=""),
        "PORT": config("DB_PORT", default=""),
    }
}

# ---------------------------------------------------------------------------
# CORS / CSRF
# ---------------------------------------------------------------------------

_DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8080",
    "https://integraoci.supercentro.rio.br",
]

CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_NAME = "csrftoken"
CSRF_USE_SESSIONS = config("CSRF_USE_SESSIONS", default=False, cast=bool)
CSRF_COOKIE_HTTPONLY = config("CSRF_COOKIE_HTTPONLY", default=False, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
CSRF_COOKIE_SAMESITE = config("CSRF_COOKIE_SAMESITE", default="None")

CORS_ALLOWED_ORIGINS = list(
    dict.fromkeys(
        _DEFAULT_ORIGINS + list(config("CORS_ALLOWED_ORIGINS", default="", cast=Csv()))
    )
)
CSRF_TRUSTED_ORIGINS = list(
    dict.fromkeys(
        _DEFAULT_ORIGINS + list(config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv()))
    )
)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "Content-Type",
    "X-API-KEY",
    "X-USER-NAME",
]

# ---------------------------------------------------------------------------
# Autenticação — SimpleJWT
# ---------------------------------------------------------------------------

AUTH_USER_MODEL = "auth.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=config("JWT_ACCESS_MINUTES", default=60, cast=int)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

TOKEN_EXPIRATION_TIME = config("TOKEN_EXPIRATION_TIME", default=86400, cast=int)

# ---------------------------------------------------------------------------
# Cache (Redis — requerido para rate-limiting e limpeza automática)
# ---------------------------------------------------------------------------

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_CACHE_DB = int(os.environ.get("REDIS_CACHE_DB", 1))

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
        "KEY_PREFIX": "integra_oci",
        "TIMEOUT": 300,
    }
}

# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

DATA_UPLOAD_MAX_MEMORY_SIZE = config("DATA_UPLOAD_MAX_MEMORY_SIZE", default=209715200, cast=int)  # 200 MB
DATA_UPLOAD_MAX_NUMBER_FILES = config("DATA_UPLOAD_MAX_NUMBER_FILES", default=50, cast=int)

# ---------------------------------------------------------------------------
# Banco MySQL externo — tabela SIGTAP (busca de nomes de procedimentos)
# ---------------------------------------------------------------------------
# Opcional: se não configurado, os nomes de procedimentos não são resolvidos.
# MYSQL_DATA_HOST=...  MYSQL_DATA_USER=...  MYSQL_DATA_PASSWORD=...
# MYSQL_DATA_DB=...    MYSQL_DATA_PORT=3306

# ---------------------------------------------------------------------------
# Artefatos BPA/APAC gerados pelo módulo
# ---------------------------------------------------------------------------

MEDIA_ROOT = str(BASE_DIR)
BPA_APAC_ARTIFACT_RETENTION_DAYS = config("BPA_APAC_ARTIFACT_RETENTION_DAYS", default=90, cast=int)
BPA_APAC_AUTO_CLEANUP = config("BPA_APAC_AUTO_CLEANUP", default=True, cast=bool)

# ---------------------------------------------------------------------------
# Arquivos estáticos
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = []
STATICFILES_STORAGE = "whitenoise.storage.GzipManifestStaticFilesStorage"
WHITENOISE_MAX_AGE = 31536000

# ---------------------------------------------------------------------------
# Internacionalização
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:5173")
