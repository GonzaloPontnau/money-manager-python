"""
Archivo de inicialización del proyecto Django.
Este archivo permite configurar conexiones a bases de datos alternativas.
"""

import logging

logger = logging.getLogger(__name__)

# Usar PyMySQL como alternativa a MySQLdb
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    logger.debug("PyMySQL instalado como sustituto de MySQLdb")
except ImportError:
    pass
