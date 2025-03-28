"""
Django settings for money_manager project.

Generated by 'django-admin startproject' using Django 5.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))  # Carga .env primero si existe

# Detectar entorno Vercel
ON_VERCEL = os.environ.get('VERCEL') == '1'

# Determinar si usar Turso
USE_TURSO = os.environ.get('USE_TURSO', 'False').lower() == 'true'
TURSO_URL = os.environ.get('TURSO_URL')
TURSO_AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

# Configuración por defecto (SQLite local)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 600,  # Buena práctica mantenerlo
    }
}

# 1. Prioridad: Usar Turso si está activado y configurado
if USE_TURSO:
    if TURSO_URL and TURSO_AUTH_TOKEN:
        print("INFO: Configurando base de datos para usar Turso.")
        DATABASES['default'] = {
            'ENGINE': 'money_manager.db_backends.turso',
            # Usar /tmp para el archivo de réplica local en Vercel
            'NAME': '/tmp/local_replica.db3' if ON_VERCEL else BASE_DIR / 'local_replica.db3',
            'TURSO_URL': TURSO_URL,
            'TURSO_AUTH_TOKEN': TURSO_AUTH_TOKEN,
            'CONN_MAX_AGE': 600,
        }
    else:
        print("ADVERTENCIA: USE_TURSO=true pero faltan TURSO_URL o TURSO_AUTH_TOKEN. Usando SQLite local.")

# 2. Si no se usa Turso, pero existe DATABASE_URL, usar dj_database_url
elif DATABASE_URL:
    print(f"INFO: Configurando base de datos desde DATABASE_URL: {DATABASE_URL[:30]}...")
    db_from_env = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )

    # Corrección específica para SQLite vía URL para evitar errores con SSL o path
    if db_from_env.get('ENGINE') == 'django.db.backends.sqlite3':
        # Si es SQLite en Vercel vía URL, forzar /tmp si el path no es absoluto
        db_name = db_from_env.get('NAME', '')
        if ON_VERCEL and db_name and not os.path.isabs(db_name):
            print(f"WARN: SQLite DB name '{db_name}' no es absoluto en Vercel, usando '/tmp/{db_name}'")
            db_from_env['NAME'] = f'/tmp/{os.path.basename(db_name)}'  # Ponerlo en /tmp

        # Eliminar opciones incompatibles con SQLite
        if 'OPTIONS' in db_from_env:
            for param in ['sslmode', 'ssl_require', 'ssl_ca', 'ssl_cert', 'ssl_key']:
                if param in db_from_env['OPTIONS']:
                    del db_from_env['OPTIONS'][param]
            # Si OPTIONS queda vacío, eliminarlo
            if not db_from_env['OPTIONS']:
                del db_from_env['OPTIONS']

    DATABASES['default'].update(db_from_env)

    # Soporte PyMySQL si es MySQL
    if DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        try:
            import pymysql
            pymysql.install_as_MySQLdb()
            print("INFO: PyMySQL instalado como driver MySQL.")
        except ImportError:
            print("ADVERTENCIA: El backend es MySQL pero pymysql no está instalado.")

# 3. Si estamos en Vercel, no se usó Turso ni DATABASE_URL, usar SQLite en /tmp por defecto
elif ON_VERCEL:
    print("INFO: Entorno Vercel detectado sin Turso/DATABASE_URL. Usando SQLite en /tmp por defecto.")
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/default_vercel.db3',  # Ruta escribible
        'CONN_MAX_AGE': 600,
    }

# 4. Si no se usa Turso ni DATABASE_URL, ya está configurado SQLite local (por defecto)
else:
    print("INFO: Usando configuración de base de datos SQLite local por defecto.")

# Imprimir el motor final para depuración
print(f"INFO: Motor de base de datos final: {DATABASES['default']['ENGINE']}")
print(f"INFO: Nombre/Path de base de datos final: {DATABASES['default'].get('NAME')}")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'una-clave-secreta-por-defecto-solo-para-desarrollo')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
VERCEL_URL = os.environ.get('VERCEL_URL')
if VERCEL_URL:
    from urllib.parse import urlparse
    parsed_url = urlparse(f"https://{VERCEL_URL}")
    hostname = parsed_url.hostname
    if hostname:
        ALLOWED_HOSTS.append(hostname)

# IMPORTANTE para POST en HTTPS (Login/Registro en Vercel)
CSRF_TRUSTED_ORIGINS = []
if VERCEL_URL:
    CSRF_TRUSTED_ORIGINS.append(f"https://{VERCEL_URL}")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'finanzas.apps.FinanzasConfig',  # Nuestra aplicación
    'turso_integration',  # Aplicación para integrar Turso
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise debe ir JUSTO DESPUÉS de SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.gzip.GZipMiddleware',  # Comprimir respuestas
    'finanzas.middleware.CachingMiddleware',  # Nuestro middleware personalizado
]

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

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_TZ = True

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