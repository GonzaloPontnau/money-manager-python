#!/bin/bash
# Script para crear archivos estáticos y ejecutar migraciones
echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Recogiendo archivos estáticos..."
python manage.py collectstatic --noinput

echo "Ejecutando migraciones..."
# Usamos la conexión directa para migraciones, que es más estable
python manage.py migrate

echo "Construcción completada"
