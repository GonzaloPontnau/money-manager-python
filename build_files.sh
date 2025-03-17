#!/bin/bash
# Script para crear archivos estáticos y ejecutar migraciones

echo "Usando Python de Vercel..."
# En Vercel, necesitamos usar la ruta completa a los ejecutables
which python
which pip

echo "Instalando dependencias..."
/opt/vercel/python3/bin/python -m pip install -r requirements.txt

echo "Creando directorio de estáticos..."
mkdir -p staticfiles

echo "Copiando archivos estáticos manualmente..."
cp -r static/* staticfiles/

echo "Generando archivo para verificar directorio..."
echo "/* Archivo generado automáticamente */" > staticfiles/styles.css
cat static/css/styles.css >> staticfiles/styles.css

echo "Construcción completada"
touch staticfiles/.gitkeep
