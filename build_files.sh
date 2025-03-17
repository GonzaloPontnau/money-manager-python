#!/bin/bash
# Script para crear archivos estáticos y ejecutar migraciones

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Creando directorio de estáticos..."
mkdir -p staticfiles

echo "Recogiendo archivos estáticos..."
python manage.py collectstatic --noinput

echo "Ejecutando migraciones..."
python manage.py migrate

echo "Construcción completada"
touch staticfiles/.gitkeep
