"""
Script para ayudar con la configuración de la base de datos.
"""
import os
import sys
from pathlib import Path

def main():
    """Función principal para ayudar con la configuración de la base de datos."""
    print("=== Asistente de configuración de base de datos ===")
    
    # Detectar ubicación del proyecto
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Verificar si se quiere usar Turso
    use_turso = os.environ.get('USE_TURSO', 'False').lower() == 'true'
    
    if use_turso:
        print("Configuración para Turso detectada.")
        turso_url = os.environ.get('TURSO_URL')
        turso_auth_token = os.environ.get('TURSO_AUTH_TOKEN')
        
        if not turso_url or not turso_auth_token:
            print("ADVERTENCIA: Faltan variables de entorno para Turso.")
            print("Por favor configura TURSO_URL y TURSO_AUTH_TOKEN en tu archivo .env")
        else:
            print(f"URL de Turso configurada: {turso_url}")
            print("Token de autorización de Turso configurado.")
            
            # Verificar si tenemos libsql_experimental
            try:
                import libsql_experimental
                print(f"✅ libsql-experimental está instalado (versión: {getattr(libsql_experimental, '__version__', 'desconocida')})")
            except ImportError:
                print("❌ libsql-experimental no está instalado.")
                print("Para instalar: pip install libsql-experimental>=0.0.44")
                
            # Verificar si el backend de Turso está configurado correctamente
            backend_dir = os.path.join(BASE_DIR, 'money_manager', 'db_backends', 'turso')
            base_file = os.path.join(backend_dir, 'base.py')
            
            if os.path.exists(base_file):
                print("✅ Backend de Turso está configurado correctamente.")
            else:
                print("❌ El backend de Turso no está configurado correctamente.")
                print(f"Verifica que exista el archivo: {base_file}")
    else:
        print("Usando SQLite estándar (USE_TURSO=False).")
        
    print("\n=== Recomendaciones ===")
    print("1. Para desarrollo local con SQLite estándar:")
    print("   - No se requiere configuración adicional")
    print("2. Para desarrollo local con Turso:")
    print("   - Configura USE_TURSO=True en .env")
    print("   - Configura TURSO_URL y TURSO_AUTH_TOKEN en .env")
    print("   - Instala: pip install libsql-experimental>=0.0.44")
    print("3. Para Vercel:")
    print("   - Se recomienda USE_TURSO=False")
    print("   - Asegúrate de que vercel.json tiene la configuración correcta")
    
    print("\n=== Finalizado ===")

if __name__ == "__main__":
    main()
