"""
Script para inicializar la base de datos Turso con el esquema necesario.
"""
import os
import sys
import libsql_experimental as libsql
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def main():
    """Función principal que inicializa la base de datos"""
    turso_url = os.environ.get('TURSO_URL')
    turso_auth_token = os.environ.get('TURSO_AUTH_TOKEN')
    
    if not turso_url or not turso_auth_token:
        print("Error: Las variables TURSO_URL y TURSO_AUTH_TOKEN deben estar configuradas")
        sys.exit(1)
    
    print(f"Conectando a Turso en: {turso_url}")
    
    # Conectar a la base de datos
    conn = libsql.connect(
        "local.db",
        sync_url=turso_url,
        auth_token=turso_auth_token
    )
    
    try:
        # Sincronizar primero para obtener los datos más recientes
        conn.sync()
        print("Conexión establecida y sincronizada con Turso")
        
        # Aquí puedes ejecutar las consultas SQL necesarias para crear el esquema
        # Por ejemplo:
        # conn.execute("CREATE TABLE IF NOT EXISTS auth_user (id INTEGER PRIMARY KEY, ...)")
        # conn.execute("CREATE TABLE IF NOT EXISTS finanzas_categoria (id INTEGER PRIMARY KEY, ...)")
        
        # Sincronizar para guardar los cambios
        conn.sync()
        print("Base de datos inicializada correctamente")
        
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
