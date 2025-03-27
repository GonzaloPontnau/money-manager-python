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
        if not LIBSQL_AVAILABLE:
            # Si libsql no está disponible, usar SQLite estándar y registrar advertencia
            logger.warning("Usando SQLite estándar sin sincronización con Turso. Instala libsql-experimental para sincronización.")
            return super().get_new_connection(conn_params)
            
        # Si llegamos aquí, libsql está disponible
        turso_url = self.settings_dict.get('TURSO_URL')
        turso_auth_token = self.settings_dict.get('TURSO_AUTH_TOKEN')
        
        if not turso_url or not turso_auth_token:
            logger.warning("TURSO_URL o TURSO_AUTH_TOKEN no configurados. Usando SQLite sin sincronización.")
            return super().get_new_connection(conn_params)
        
        logger.info(f"Conectando a Turso en: {turso_url}")
        
        try:
            # Verificar si el API de conexión ha cambiado entre versiones
            if hasattr(libsql, 'connect'):
                conn = libsql.connect(
                    database=conn_params['database'],
                    sync_url=turso_url,
                    auth_token=turso_auth_token
                )
            else:
                # Versiones anteriores podrían tener una API diferente
                logger.warning("Usando API alternativa para conectar con Turso")
                conn = super().get_new_connection(conn_params)
                
            # Verificar si el método sync existe antes de llamarlo
            if hasattr(conn, 'sync'):
                conn.sync()
                logger.info("Conexión establecida y sincronizada con Turso")
            else:
                logger.warning("El método 'sync' no está disponible en esta versión de libsql")
                
            return conn
        except Exception as e:
            logger.error(f"Error al conectar con Turso: {e}")
            logger.warning("Fallback a SQLite local")
            return super().get_new_connection(conn_params)
    
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
