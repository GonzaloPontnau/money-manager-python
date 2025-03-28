#!/bin/bash
# Script para construir archivos estáticos en Vercel

echo "Iniciando build_files.sh..."

# Configurar permisos de ejecución
chmod -R 755 .

# Instalar dependencias
pip install -r requirements.txt

# Crear directorio para archivos estáticos si no existe
mkdir -p staticfiles

# Recolectar archivos estáticos
python -m manage collectstatic --noinput

echo "Proceso de construcción completado."
