"""
Script para inicializar la base de datos Turso con el esquema necesario.
"""
import os
import sys
import sqlite3
import libsql_experimental as libsql
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv()

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(BASE_DIR, 'db.sqlite3')

def main():
    """Función principal que inicializa la base de datos"""
    turso_url = os.environ.get('TURSO_URL')
    turso_auth_token = os.environ.get('TURSO_AUTH_TOKEN')
    
    if not turso_url or not turso_auth_token:
        print("Error: Las variables TURSO_URL y TURSO_AUTH_TOKEN deben estar configuradas")
        sys.exit(1)
    
    print(f"Conectando a Turso en: {turso_url}")
    
    # Verificar si la base de datos local existe
    if not os.path.exists(DB_PATH):
        print(f"Error: La base de datos local '{DB_PATH}' no existe.")
        print("Ejecuta primero 'python manage.py migrate' para crear la base de datos local.")
        sys.exit(1)
    
    # Conectar a la base de datos
    try:
        conn = libsql.connect(
            DB_PATH,
            sync_url=turso_url,
            auth_token=turso_auth_token
        )
        
        # Sincronizar primero para obtener los datos más recientes
        conn.sync()
        print("Conexión establecida y sincronizada con Turso")
        
        # Verificar que la base de datos tiene tablas
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if tables:
            print(f"Tablas existentes: {', '.join([t[0] for t in tables if not t[0].startswith('sqlite_')])}")
        else:
            print("¡Advertencia! La base de datos no tiene tablas.")
            print("Asegúrate de haber ejecutado las migraciones: python manage.py migrate")
        
        # Sincronizar para guardar los cambios
        conn.sync()
        print("Base de datos sincronizada correctamente con Turso")
        
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
