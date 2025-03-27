"""
Script para instalar las dependencias en Windows, incluyendo libsql-experimental.
"""
import os
import sys
import subprocess
import platform

def check_dependencies():
    """Verifica que las dependencias necesarias estén instaladas."""
    missing = []
    
    try:
        import pip
    except ImportError:
        missing.append("pip")
    
    try:
        import wheel
    except ImportError:
        missing.append("wheel")
    
    try:
        import setuptools
    except ImportError:
        missing.append("setuptools")
    
    return missing

def install_basics():
    """Instala las dependencias básicas necesarias para la compilación."""
    missing = check_dependencies()
    
    if missing:
        print(f"Instalando dependencias básicas: {', '.join(missing)}")
        for dep in missing:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

def install_requirements():
    """Instala las dependencias del proyecto desde requirements.txt."""
    print("Instalando dependencias del proyecto...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencias básicas instaladas correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error instalando dependencias: {e}")
        sys.exit(1)

def install_libsql_manually():
    """Intenta instalar libsql-experimental usando múltiples métodos."""
    methods = [
        # Método 1: Instalación directa
        [sys.executable, "-m", "pip", "install", "libsql-experimental"],
        
        # Método 2: Con opciones adicionales
        [sys.executable, "-m", "pip", "install", "libsql-experimental", "--no-cache-dir"],
        
        # Método 3: Con compilación forzada
        [sys.executable, "-m", "pip", "install", "libsql-experimental", "--no-binary", ":all:"],
    ]
    
    for i, cmd in enumerate(methods, 1):
        print(f"\nIntentando instalar libsql-experimental (método {i}/{len(methods)})...")
        try:
            subprocess.check_call(cmd)
            print("¡libsql-experimental instalado correctamente!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Falló el método {i}: {e}")
    
    print("\nNo se pudo instalar libsql-experimental automáticamente.")
    print("El proyecto funcionará con SQLite pero sin sincronización con Turso.")
    return False

def main():
    """Función principal del script."""
    if platform.system() != "Windows":
        print("Este script está diseñado para Windows. En otros sistemas, usa pip install normalmente.")
        sys.exit(1)
    
    print("=== Instalador de dependencias para Windows ===")
    
    # Paso 1: Instalar dependencias básicas
    install_basics()
    
    # Paso 2: Instalar dependencias del proyecto
    install_requirements()
    
    # Paso 3: Intentar instalar libsql-experimental
    try:
        import libsql_experimental
        print("libsql-experimental ya está instalado. No es necesario reinstalarlo.")
    except ImportError:
        success = install_libsql_manually()
        if not success:
            print("\nRecomendación: Modifica .env para deshabilitar Turso:")
            print("USE_TURSO=False")
    
    print("\n=== Instalación completada ===")
    print("Ahora puedes ejecutar: python manage.py migrate")

if __name__ == "__main__":
    main()
