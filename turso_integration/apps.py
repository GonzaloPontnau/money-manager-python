from django.apps import AppConfig

class TursoIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'turso_integration'
    verbose_name = "Integración con SQLite"
    
    def ready(self):
        """
        Inicialización al arrancar la aplicación.
        """
        # Usando SQLite estándar
        pass
