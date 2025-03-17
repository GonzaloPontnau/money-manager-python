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

echo "Asegurando que styles.css está en la raíz de staticfiles..."
# Crear styles.css directamente en la raíz para coincidir con la referencia en los templates
echo "/* Archivo generado automáticamente para Vercel */" > staticfiles/styles.css
cat static/css/styles.css >> staticfiles/styles.css

echo "Asegurando que css/styles.css también existe para referencias locales..."
mkdir -p staticfiles/css
cp static/css/styles.css staticfiles/css/styles.css

echo "Construcción completada"
touch staticfiles/.gitkeep

# Listar archivos para debug
echo "Contenido de staticfiles:"
ls -la staticfiles
echo "Contenido de staticfiles/css (si existe):"
ls -la staticfiles/css 2>/dev/null || echo "No existe directorio css"
