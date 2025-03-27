"""
Script para instalar las dependencias necesarias en Windows.
"""
import os
import sys
import subprocess
import platform

def main():
    """Instala las dependencias necesarias para el proyecto."""
    print("Instalando dependencias del proyecto...")
    
    # Instalar dependencias básicas
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Intentar instalar libsql-experimental si estamos en Windows
    if platform.system() == "Windows":
        try:
            print("Instalando libsql-experimental en Windows...")
            # En Windows puede requerir opciones adicionales o compilación manual
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "libsql-experimental", "--no-cache-dir", "--no-binary", ":all:"
            ])
            print("libsql-experimental instalado correctamente")
        except subprocess.CalledProcessError:
            print("ADVERTENCIA: No se pudo instalar libsql-experimental.")
            print("El proyecto usará SQLite estándar sin sincronización con Turso.")
    
    print("Instalación completada.")

if __name__ == "__main__":
    main()
