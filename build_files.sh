#!/bin/bash
# Script simplificado para Vercel build

echo "Iniciando build..."

# 1. Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# 2. Ejecutar collectstatic
echo "Ejecutando collectstatic..."
python manage.py collectstatic --noinput --clear

echo "Build completado."

# Listar para debug en logs de Vercel
echo "Contenido de staticfiles recolectado:"
ls -la staticfiles
