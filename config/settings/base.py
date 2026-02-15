import logging
import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger("config.settings")

APP_ENV = os.environ.get("APP_ENV", os.environ.get("DJANGO_ENV", "development")).lower()
ON_VERCEL = os.environ.get("VERCEL") == "1"

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "CONN_MAX_AGE": 600,
    }
}

if DATABASE_URL:
    db_from_env = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )

    if db_from_env.get("ENGINE") == "django.db.backends.sqlite3":
        db_name = db_from_env.get("NAME", "")
        if ON_VERCEL and db_name and not os.path.isabs(db_name):
            db_from_env["NAME"] = f"/tmp/{os.path.basename(db_name)}"

        if "OPTIONS" in db_from_env:
            for param in ["sslmode", "ssl_require", "ssl_ca", "ssl_cert", "ssl_key"]:
                db_from_env["OPTIONS"].pop(param, None)
            if not db_from_env["OPTIONS"]:
                del db_from_env["OPTIONS"]

    DATABASES["default"].update(db_from_env)

    if DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
        try:
            import pymysql

            pymysql.install_as_MySQLdb()
            logger.info("PyMySQL installed as MySQL driver")
        except ImportError:
            logger.warning("MySQL configured but pymysql is not installed")
elif ON_VERCEL:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/tmp/default_vercel.db3",
        "CONN_MAX_AGE": 600,
    }

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
allowed_hosts_env = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]
ALLOWED_HOSTS.extend([h for h in allowed_hosts_env if h not in ALLOWED_HOSTS])

production_hostname = os.environ.get("PRODUCTION_HOSTNAME", "money-manager-nine-umber.vercel.app")
if production_hostname and production_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(production_hostname)

vercel_url = os.environ.get("VERCEL_URL")
if vercel_url:
    hostname = urlparse(f"https://{vercel_url}").hostname
    if hostname and hostname not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(hostname)

csrf_env = [o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(csrf_env))
if production_hostname:
    origin = f"https://{production_hostname}"
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)
if vercel_url:
    origin = f"https://{urlparse(f'https://{vercel_url}').hostname}"
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "api.apps.ApiConfig",
    "finanzas.apps.FinanzasConfig",
    "chatbot.apps.ChatbotConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "finanzas.middleware.CachingMiddleware",
    "finanzas.middleware.AdminAutoLoginMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "frontend" / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-es"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "frontend" / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "money-manager-cache",
    }
}

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120")
QDRANT_URL = os.environ.get("QDRANT_URL", "")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", "")
HF_API_TOKEN = os.environ.get("HUGGINGFACE_API_KEY", os.environ.get("HF_API_TOKEN", ""))
CHATBOT_MAX_HISTORY = int(os.environ.get("CHATBOT_MAX_HISTORY", "10"))
CHATBOT_MAX_TOKENS = int(os.environ.get("CHATBOT_MAX_TOKENS", "1024"))
CHATBOT_EMBEDDINGS_ENABLED = (
    os.environ.get("CHATBOT_EMBEDDINGS_ENABLED", "true").lower() == "true"
)

ENABLE_DEV_SEED_DATA = os.environ.get("ENABLE_DEV_SEED_DATA", "false").lower() == "true"
SEED_INITIAL_BALANCE = int(os.environ.get("SEED_INITIAL_BALANCE", "0"))

AUTO_LOGIN_USERNAME = os.environ.get("AUTO_LOGIN_USERNAME")

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Money Manager API",
    "DESCRIPTION": "API versionada para Money Manager",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG" if DEBUG else "INFO").upper()
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "simple",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO" if DEBUG else "WARNING", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "DEBUG" if DEBUG else "ERROR", "propagate": False},
        "config": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        "finanzas": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        "chatbot": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
    },
}
