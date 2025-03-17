#!/bin/bash
# Script para crear archivos estáticos y ejecutar migraciones

# Usar rutas explícitas a los ejecutables de Python
echo "Instalando dependencias..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Creando directorio de estáticos..."
mkdir -p staticfiles

echo "Recogiendo archivos estáticos..."
python manage.py collectstatic --noinput

echo "Ejecutando migraciones..."
python manage.py migrate

echo "Construcción completada"
touch staticfiles/.gitkeep
