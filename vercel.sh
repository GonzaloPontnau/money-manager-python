#!/bin/bash

# Asegurar que los comandos fallen en errores
set -e

echo "VERCEL_ENV: $VERCEL_ENV"
echo "PYTHON_VERSION: $(python --version)"
echo "NODE_VERSION: $(node --version)"

# Instalar dependencias de Python
echo "Instalando dependencias de Python..."
pip install -r requirements.txt -v

# Crear directorios necesarios
echo "Creando directorios estáticos..."
mkdir -p staticfiles
mkdir -p mediafiles

# Colectar estáticos (si usas Django/Flask)
# echo "Colectando estáticos..."
# python manage.py collectstatic --noinput  # Para Django

# Copia manual de estáticos (alternativa)
if [ -d "static" ]; then
    echo "Copiando archivos estáticos..."
    cp -r static/* staticfiles/
    echo "Estáticos copiados:"
    find staticfiles -type f | sort
fi

# Verificar estructura
echo "Estructura del proyecto:"
tree -L 3