from django.apps import AppConfig


class FinanzasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finanzas'

    def ready(self):
        try:
            # Importar signals de manera segura
            import finanzas.signals
        except ImportError:
            # Si hay un error al importar, simplemente lo registramos
            # pero no bloqueamos la inicialización de la aplicación
            print("Advertencia: No se pudieron cargar las señales de la aplicación finanzas.")
