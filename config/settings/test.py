from .base import *  # noqa: F401,F403

DEBUG = False

if not SECRET_KEY:
    SECRET_KEY = "test-only-secret-key-change-me-32-chars-minimum"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CHATBOT_EMBEDDINGS_ENABLED = False
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles-test"
STATIC_ROOT.mkdir(parents=True, exist_ok=True)

