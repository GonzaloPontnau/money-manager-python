"""
Backend de base de datos para Turso en Django.
Extiende el backend SQLite de Django para trabajar con la API de Turso.
"""

import os
import logging
import warnings
from django.db.backends.sqlite3.base import DatabaseWrapper as SQLiteDatabaseWrapper
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('django.db.backends.turso')

# Manejo seguro de la importación de libsql_experimental
try:
    import libsql_experimental as libsql
    LIBSQL_AVAILABLE = True
    logger.info(f"libsql_experimental cargado correctamente (versión: {getattr(libsql, '__version__', 'desconocida')})")
except ImportError as e:
    LIBSQL_AVAILABLE = False
    error_msg = str(e)
    warnings.warn(
        f"No se pudo importar libsql_experimental: {error_msg}. Usando SQLite estándar como fallback. "
        "Para sincronización con Turso, instala: pip install libsql-experimental"
    )

class DatabaseWrapper(SQLiteDatabaseWrapper):
    """Wrapper de la base de datos para Turso"""
    
    vendor = 'turso'
    display_name = 'Turso/SQLite'
    
    def get_new_connection(self, conn_params):
        """
        Establece una conexión con la base de datos Turso.
        Si libsql no está disponible, usa SQLite estándar.
        """
        settings_dict = self.settings_dict
        turso_url = settings_dict.get('TURSO_URL')
        auth_token = settings_dict.get('TURSO_AUTH_TOKEN')
        # Obtén el valor de NAME, que podría ser Path o string
        db_name_value = settings_dict.get('NAME')

        if turso_url and auth_token:
            if not db_name_value:
                # Es buena idea requerir NAME para la réplica local
                raise ImproperlyConfigured("Database 'NAME' must be set for Turso embedded replica backend.")

            # Convertir explícitamente a string si es un objeto Path
            local_db_path = str(db_name_value)
            
            try:
                print(f"INFO: [Turso Backend] Connecting: db='{local_db_path}', sync_url='{turso_url[:20]}...', token='***'")
                conn = libsql.connect(
                    database=local_db_path,  # Ahora pasamos un string
                    sync_url=turso_url,
                    auth_token=auth_token,
                )
                print("INFO: [Turso Backend] Connection successful.")
                return conn
            except Exception as e:
                print(f"ERROR: [Turso Backend] Error connecting to Turso: {e}", file=sys.stderr)
                raise OperationalError(f"Failed to connect to Turso: {e}") from e
        else:
            # Lógica de fallback
            print("WARN: [Turso Backend] Turso URL/Token missing. Falling back to SQLite.")
            # Convertir también el parámetro database a string en el fallback
            fallback_params = conn_params.copy()
            if 'database' in fallback_params and hasattr(fallback_params['database'], '__fspath__'):
                fallback_params['database'] = str(fallback_params['database'])
            
            try:
                return super().get_new_connection(fallback_params)
            except Exception as fallback_e:
                print(f"ERROR: [Turso Backend] Fallback connection failed: {fallback_e}", file=sys.stderr)
                raise OperationalError(f"Fallback connection failed: {fallback_e}") from fallback_e
    
    def _set_autocommit(self, autocommit):
        """
        Configurar el modo autocommit.
        En Turso, necesitamos sincronizar después de cada commit.
        """
        super()._set_autocommit(autocommit)
        
        # Solo intentar sincronizar si estamos usando Turso
        if LIBSQL_AVAILABLE and hasattr(self.connection, 'sync') and autocommit:
            try:
                self.connection.sync()
            except Exception as e:
                logger.error(f"Error al sincronizar Turso después de activar autocommit: {e}")
    
    def _commit(self):
        """
        Realizar commit y sincronizar con Turso si está disponible.
        """
        super()._commit()
        
        # Solo intentar sincronizar si estamos usando Turso
        if LIBSQL_AVAILABLE and hasattr(self.connection, 'sync'):
            try:
                self.connection.sync()
            except Exception as e:
                logger.error(f"Error al sincronizar Turso después de commit: {e}")
