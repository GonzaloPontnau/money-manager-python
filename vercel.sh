#!/bin/bash

echo "VERCEL_ENV: $VERCEL_ENV"
echo "PYTHON_VERSION: $(python --version)"
echo "NODE_VERSION: $(node --version)"

# Instalar dependencias
pip install -r requirements.txt

# Crear directorio para archivos estáticos
mkdir -p staticfiles

# Copiar archivos estáticos manualmente
if [ -d "static" ]; then
    cp -r static/* staticfiles/
    echo "Archivos estáticos copiados correctamente"
fi

# Generar un archivo de verificación
echo "/* Archivo de verificación para Vercel */" > staticfiles/vercel.css
