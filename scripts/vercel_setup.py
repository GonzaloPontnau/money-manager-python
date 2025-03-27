"""
Script para configurar el entorno en Vercel.
Este script ayuda a establecer configuraciones específicas para Vercel.
"""
import os
import sys
import json
from pathlib import Path

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

def main():
    """Configurar el entorno para Vercel."""
    print("=== Configurando entorno para Vercel ===")
    
    # Forzar USE_TURSO a False en Vercel
    os.environ['USE_TURSO'] = 'False'
    print("Integración con Turso desactivada para Vercel.")
    
    # Verificar si estamos en Vercel
    if os.environ.get('VERCEL', '0') == '1':
        print("Detectado entorno Vercel.")
        
        # Crear un .env para Vercel si no existe
        env_path = os.path.join(BASE_DIR, '.env')
        if not os.path.exists(env_path):
            with open(env_path, 'w') as f:
                f.write("USE_TURSO=False\n")
                f.write("DEBUG=False\n")
            print("Archivo .env creado para Vercel.")
    
    print("\n=== Configuración completada ===")
    print("La aplicación usará SQLite sin sincronización con Turso en Vercel.")

if __name__ == "__main__":
    main()
