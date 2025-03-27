"""
Script para verificar y preparar la base de datos SQLite.
"""
import os
import sys
import sqlite3
from pathlib import Path

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(BASE_DIR, 'db.sqlite3')

def main():
    """Función principal para verificar y preparar la base de datos SQLite."""
    print(f"=== Verificando base de datos SQLite en: {DB_PATH} ===")
    
    # Comprobar si la base de datos ya existe
    if os.path.exists(DB_PATH):
        print("La base de datos SQLite ya existe.")
        check_database()
    else:
        print("La base de datos SQLite no existe todavía.")
        print("Se creará automáticamente cuando ejecutes: python manage.py migrate")
    
    print("\n=== Consejos para trabajar con SQLite ===")
    print("1. Ejecuta 'python manage.py migrate' para crear o actualizar la estructura")
    print("2. Para ver la estructura: python manage.py inspectdb > models_auto.py")
    print("3. Asegúrate de tener permisos de escritura en la carpeta del proyecto")
    
    print("\n=== Instrucciones para Vercel ===")
    print("En Vercel, la base de datos SQLite es de solo lectura en producción.")
    print("Opciones:")
    print("1. Subir una base de datos pre-poblada con datos básicos")
    print("2. Usar un servicio de base de datos externo configurable via DATABASE_URL")
    
    print("\n=== Listo para continuar ===")

def check_database():
    """Verifica la base de datos SQLite existente."""
    try:
        # Intentar conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si hay tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if tables:
            print(f"Tablas existentes: {', '.join([t[0] for t in tables if not t[0].startswith('sqlite_')])}")
        else:
            print("La base de datos existe pero no tiene tablas.")
            
        conn.close()
    except sqlite3.Error as e:
        print(f"Error al verificar la base de datos: {e}")

if __name__ == "__main__":
    main()
