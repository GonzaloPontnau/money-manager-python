"""
Archivo de inicialización del proyecto Django.
Este archivo permite configurar conexiones a bases de datos alternativas.
"""

# Usar PyMySQL como alternativa a MySQLdb
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("PyMySQL instalado como sustituto de MySQLdb")
except ImportError:
    pass
