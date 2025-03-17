#!/bin/bash
# Script para crear archivos estáticos y ejecutar migraciones

echo "Usando Python de Vercel..."
# En Vercel, necesitamos usar la ruta completa a los ejecutables
which python
which pip

echo "Instalando dependencias..."
/opt/vercel/python3/bin/python -m pip install -r requirements.txt

echo "Creando directorios de estáticos..."
mkdir -p staticfiles
mkdir -p staticfiles/css
mkdir -p staticfiles/js
mkdir -p staticfiles/img

echo "Copiando archivos estáticos manualmente..."
if [ -d "static" ]; then
  cp -r static/* staticfiles/
fi

echo "Generando styles.css en la raíz de staticfiles..."
echo "/* Archivo generado automáticamente para Vercel - $(date) */" > staticfiles/styles.css
if [ -f "static/css/styles.css" ]; then
  cat static/css/styles.css >> staticfiles/styles.css
else
  echo "/* Archivo CSS base no encontrado - creando una versión mínima */" >> staticfiles/styles.css
  echo ":root {
    --primary-color: #6C5CE7;
    --primary-light: #8A7AFF;
    --secondary-color: #00B894;
    --dark-color: #13131A;
    --medium-dark: #1E1E26;
    --light-dark: #2D2D3A;
    --text-color: #E2E2E2;
    --text-muted: #ADADAD;
    --border-color: #3F3F50;
  }" >> staticfiles/styles.css
fi

echo "Asegurando que css/styles.css también existe..."
mkdir -p staticfiles/css
cp staticfiles/styles.css staticfiles/css/styles.css

# Asegurar que el archivo vercel.css también se procesa correctamente
if [ -f "static/css/vercel.css" ]; then
  echo "Procesando vercel.css..."
  # Reemplazar @import url('styles.css') con el contenido real del archivo
  sed -i 's|@import url(.styles.css.);|/* Contenido importado de styles.css */|' staticfiles/css/vercel.css
  cat staticfiles/css/styles.css >> staticfiles/css/vercel.css
fi

echo "Creando archivo de test para verificar que los estáticos funcionan..."
echo "<html><body><h1>Archivos estáticos funcionando</h1></body></html>" > staticfiles/test.html

echo "Construcción completada"
touch staticfiles/.gitkeep

# Listar archivos para debug
echo "Contenido de staticfiles:"
ls -la staticfiles
echo "Contenido de staticfiles/css:"
ls -la staticfiles/css 2>/dev/null || echo "No existe directorio css"
