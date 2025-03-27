import os
from django.apps import AppConfig

class TursoIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'turso_integration'
    verbose_name = "Integración con Turso"
    
    def ready(self):
        """
        Inicialización al arrancar la aplicación.
        """
        # Verificar si debemos usar Turso
        use_turso = os.environ.get('USE_TURSO', 'False').lower() == 'true'
        
        if use_turso:
            # Verificar que tenemos las variables necesarias
            turso_url = os.environ.get('TURSO_URL')
            turso_auth_token = os.environ.get('TURSO_AUTH_TOKEN')
            
            if not turso_url or not turso_auth_token:
                print("ADVERTENCIA: USE_TURSO está activado pero faltan TURSO_URL o TURSO_AUTH_TOKEN")
            else:
                print(f"Integración con Turso activada. URL: {turso_url}")
                
                # Intentar cargar libsql_experimental
                try:
                    import libsql_experimental
                    print("libsql_experimental cargado correctamente")
                except ImportError:
                    print("ERROR: No se pudo cargar libsql_experimental. Instálalo con: pip install libsql-experimental")
        else:
            print("Integración con Turso desactivada. Usando SQLite estándar.")
