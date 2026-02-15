import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()

if os.environ.get("VERCEL") == "1" and not os.environ.get("DATABASE_URL"):
    # On Vercel without a real specific DATABASE_URL, we are using ephemeral sqlite
    # which is empty since it's created in /tmp on every execution.
    # We must run migrate to create tables, otherwise app crashes.
    from django.core.management import call_command
    try:
        call_command("migrate")
    except Exception as e:
        print(f"Migration failed: {e}")

