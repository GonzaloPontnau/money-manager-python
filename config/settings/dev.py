from .base import *  # noqa: F401,F403

DEBUG = True

if not SECRET_KEY:
    SECRET_KEY = "dev-only-insecure-key-change-me-32-chars-minimum"

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

