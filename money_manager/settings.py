"""
Django settings for money_manager project.

Generated by 'django-admin startproject' using Django 5.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'ZteozxDKhtDSmUxxWnRaK0qt4-osWirNtPnhHrhTbaKS-A5A6DhFsKSiCtz_KxAFrKw')

# SECURITY WARNING: don't run with debug turned on in production!
# Temporalmente habilitamos DEBUG para diagnosticar errores
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.vercel.app', '.now.sh']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'finanzas.apps.FinanzasConfig',  # Nuestra aplicación
    # 'crispy_forms',  # Para formularios con mejor aspecto
    # 'crispy_bootstrap4',  # Bootstrap 4 para crispy-forms
]

# Añadir libsql-experimental a las aplicaciones instaladas para asegurar que se carga correctamente
INSTALLED_APPS += [
    'turso_integration',  # Aplicación para integrar Turso
]

# Detectar si estamos en Vercel
ON_VERCEL = os.environ.get('VERCEL', False)

# Lista base de middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.gzip.GZipMiddleware',  # Comprimir respuestas
    'finanzas.middleware.CachingMiddleware',  # Nuestro middleware personalizado
]

# Configuración para archivos estáticos
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'  # Para versioning de archivos estáticos

# Añadir WhiteNoise solo si estamos en Vercel o si está explícitamente instalado
try:
    import whitenoise
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    if not DEBUG:
        STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
except ImportError:
    # WhiteNoise no está instalado, usamos el storage predeterminado
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

ROOT_URLCONF = 'money_manager.urls'

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

WSGI_APPLICATION = 'money_manager.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Detectar si debemos usar Turso
USE_TURSO = os.environ.get('USE_TURSO', 'False').lower() == 'true'
TURSO_URL = os.environ.get('TURSO_URL')
TURSO_AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN')

# Configuración base para SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'CONN_MAX_AGE': 60,  # Mantener conexiones activas por 60 segundos
    }
}

# Si Turso está activado y tenemos las credenciales, usar el backend personalizado
if USE_TURSO and TURSO_URL and TURSO_AUTH_TOKEN:
    DATABASES['default'] = {
        'ENGINE': 'money_manager.db_backends.turso',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'TURSO_URL': TURSO_URL,
        'TURSO_AUTH_TOKEN': TURSO_AUTH_TOKEN,
        'CONN_MAX_AGE': 60,
    }
    print(f"Usando backend de Turso para la base de datos")
# Si estamos en Vercel y hay una URL de base de datos, usar esa
elif ON_VERCEL and 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True
    )
    
    # Si es MySQL, usar PyMySQL como driver
    if DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        import pymysql
        pymysql.install_as_MySQLdb()


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuración adicional para archivos estáticos
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuración para entorno de Vercel
if 'VERCEL' in os.environ:
    # Aseguramos que los archivos estáticos se sirvan correctamente en Vercel
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    
    # Usamos DEBUG False para logs más claros
    DEBUG = False
    
    # Configuración para ver errores
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'ERROR',
            },
            'django.request': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'django.template': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'django.staticfiles': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }

# Archivos de medios (subidos por usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Crispy Forms (comentado temporalmente)
# CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
# CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URL
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Configuraciones adicionales de seguridad para producción
if not DEBUG:
    # HTTPS/SSL
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# Configuración de caché
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'money-manager-cache',
    }
}