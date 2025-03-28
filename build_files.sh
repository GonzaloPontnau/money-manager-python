#!/bin/bash
# Script para Vercel build con verificación mejorada de estáticos

echo "Iniciando build..."

# 1. Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# 2. Preparar directorio de estáticos
echo "Preparando directorios..."
mkdir -p staticfiles/css
mkdir -p staticfiles/js
mkdir -p staticfiles/img

# 3. Ejecutar collectstatic con detalle
echo "Ejecutando collectstatic..."
python manage.py collectstatic --noinput --clear --verbosity 2

# 4. Verificación detallada de archivos estáticos críticos
echo "Verificando estáticos recolectados..."
echo "Contenido de staticfiles:"
ls -la staticfiles

echo "Contenido del directorio CSS:"
ls -la staticfiles/css || echo "El directorio css no existe o está vacío"

# 5. Copia de respaldo de archivos críticos (por si collectstatic falló silenciosamente)
echo "Copiando archivos críticos como respaldo..."
cp -r static/css/* staticfiles/css/ 2>/dev/null || echo "No se pudo copiar css/ (posiblemente ya existe)"

# 6. Crear archivo de verificación en la raíz de staticfiles
echo "Creando archivo de verificación..."
echo "<html><head><title>Estáticos funcionando</title></head><body><h1>Archivos estáticos verificados</h1><p>Si ves esto, la ruta a estáticos funciona.</p></body></html>" > staticfiles/static_check.html

# 7. Verificación final
echo "Verificación final:"
echo "Archivos CSS:"
ls -la staticfiles/css/
echo "¿Existe styles.css?"
ls -la staticfiles/css/styles.css 2>/dev/null || echo "No se encontró styles.css"
echo "¿Existe el archivo de prueba?"
ls -la staticfiles/test.txt 2>/dev/null || echo "No se encontró test.txt"

echo "Build completado."
