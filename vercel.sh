#!/bin/bash

echo "VERCEL_ENV: $VERCEL_ENV"
echo "PYTHON_VERSION: $(python --version)"
echo "NODE_VERSION: $(node --version)"

# Instalar dependencias con output detallado
echo "Instalando dependencias..."
pip install -r requirements.txt -v

# Crear directorio para archivos estáticos
echo "Creando directorio de estáticos..."
mkdir -p staticfiles

# Copiar archivos estáticos manualmente
if [ -d "static" ]; then
    echo "Copiando archivos estáticos..."
    cp -r static/* staticfiles/
    echo "Listando archivos estáticos copiados:"
    find staticfiles -type f | sort
fi

# Mostrar el contenido del directorio
echo "Estructura de directorios:"
find . -type d | sort

echo "Construcción completada"
