import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()

if os.environ.get("VERCEL") == "1":
    # Always run migrate on Vercel startup to ensure DB tables exist.
    # This is critical for the first deployment or when connecting a new empty DB (like Neon).
    from django.core.management import call_command
    try:
        call_command("migrate")
        print("Migration successful")
    except Exception as e:
        print(f"Migration failed: {e}")

