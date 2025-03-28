#!/bin/bash
# Script simplificado para Vercel build (confiando en collectstatic y includeFiles)

echo "Iniciando build..."

# 1. Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# 2. Ejecutar collectstatic
echo "Ejecutando collectstatic..."
python manage.py collectstatic --noinput --clear --verbosity 2 

# 3. Verificación post-collectstatic (importante para debug en logs de build)
echo "Verificando estáticos recolectados en ./staticfiles ..."
echo "Contenido raíz de staticfiles:"
ls -la staticfiles
echo "Contenido de staticfiles/css:"
ls -la staticfiles/css || echo "Directorio staticfiles/css no encontrado o vacío."
echo "¿Existe staticfiles/css/styles.css?"
ls -la staticfiles/css/styles.css 2>/dev/null || echo "ERROR: staticfiles/css/styles.css NO FUE ENCONTRADO por collectstatic."
echo "¿Existe staticfiles/favicon.ico?"
ls -la staticfiles/favicon.ico 2>/dev/null || echo "INFO: staticfiles/favicon.ico no encontrado (¿está en static/?)"

echo "Build completado."
