from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403

DEBUG = False

if not SECRET_KEY:
    if os.environ.get("VERCEL") == "1":
         SECRET_KEY = "django-insecure-vercel-demo-key-change-me-in-production"
    else:
        raise ImproperlyConfigured("SECRET_KEY must be configured in production")



if os.environ.get("VERCEL") == "1":
    ALLOWED_HOSTS = ["*"]
    # Disable manifest storage to avoid crash if collectstatic didn't run
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    # Enable DEBUG to see the actual error trace in the browser
    DEBUG = True

# Keep these if not on Vercel or if needed
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

