import logging

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class CachingMiddleware(MiddlewareMixin):
    """Secure cache headers tuned for authenticated financial data."""

    def process_response(self, request, response):
        path = request.path

        if path.startswith("/static/") or path.startswith("/staticfiles/"):
            response["Cache-Control"] = "public, max-age=31536000, immutable"
            return response

        if path.startswith("/media/"):
            response["Cache-Control"] = "private, no-store"
            return response

        if getattr(request, "user", None) and request.user.is_authenticated:
            response["Cache-Control"] = "private, no-store"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response

        if path.startswith("/admin/") or path.startswith("/login/") or path.startswith("/register/"):
            response["Cache-Control"] = "private, no-store"
            return response

        if request.method == "GET" and response.status_code == 200:
            response["Cache-Control"] = "public, max-age=60"

        return response


class AdminAutoLoginMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log in a specific user if configured.
    DANGEROUS: Use only for local development/testing.
    """

    def process_request(self, request):
        if not hasattr(request, "user") or request.user.is_authenticated:
            return

        from django.conf import settings
        from django.contrib.auth import login
        from django.contrib.auth.models import User
        from django.shortcuts import redirect

        auto_login_user = getattr(settings, "AUTO_LOGIN_USERNAME", None)

        if not auto_login_user:
            return

        try:
            user = User.objects.get(username=auto_login_user)
            login(request, user)
            logger.info(f"Auto-login successful for user: {user.username}")
            
            # If on login or register page, redirect to dashboard
            if request.path.startswith("/login/") or request.path.startswith("/register/"):
                 return redirect("finanzas:dashboard")
                 
        except User.DoesNotExist:
            logger.warning(f"Auto-login failed: User '{auto_login_user}' does not exist.")
        except Exception as e:
            logger.error(f"Auto-login error: {e}")
