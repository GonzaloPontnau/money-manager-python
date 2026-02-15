import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class FinanzasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finanzas'

    def ready(self):
        try:
            import finanzas.signals  # noqa: F401
        except ImportError:
            logger.warning("No se pudieron cargar las señales de la aplicación finanzas.")
