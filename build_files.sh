#!/bin/bash
# Script para crear archivos estáticos y ejecutar migraciones

echo "Iniciando build_files.sh..."

# Encontrar Python y pip en el PATH actual
echo "Buscando Python en el sistema..."
PYTHON_CMD=$(which python3 || which python)
PIP_CMD=$(which pip3 || which pip)

echo "Python encontrado en: $PYTHON_CMD"
echo "Pip encontrado en: $PIP_CMD"

# Instalar dependencias usando el comando de pip disponible
echo "Instalando dependencias..."
if [ -n "$PIP_CMD" ]; then
  $PIP_CMD install -r requirements.txt || echo "Error al instalar dependencias, continuando de todos modos"
else
  echo "ADVERTENCIA: pip no encontrado, omitiendo instalación de dependencias"
fi

echo "Creando directorios de estáticos..."
mkdir -p staticfiles
mkdir -p staticfiles/css
mkdir -p staticfiles/js
mkdir -p staticfiles/img

# Ejecutar collectstatic si Python está disponible
if [ -n "$PYTHON_CMD" ]; then
  echo "Ejecutando collectstatic..."
  $PYTHON_CMD manage.py collectstatic --noinput || echo "Error en collectstatic, continuando con copia manual"
fi

echo "Copiando archivos estáticos manualmente..."
if [ -d "static" ]; then
  cp -r static/* staticfiles/ || echo "Error al copiar archivos estáticos"
  echo "Archivos copiados de static/ a staticfiles/"
else
  echo "ADVERTENCIA: Directorio static/ no encontrado"
fi

echo "Generando styles.css en la raíz de staticfiles..."
echo "/* Archivo generado automáticamente para Vercel - $(date) */" > staticfiles/styles.css
if [ -f "static/css/styles.css" ]; then
  cat static/css/styles.css >> staticfiles/styles.css
  echo "styles.css generado desde static/css/styles.css"
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
  }
  
  body {
    background-color: #1A1A25;
    color: #E2E2E2;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
  }" >> staticfiles/styles.css
  echo "styles.css mínimo creado"
fi

echo "Asegurando que css/styles.css también existe..."
mkdir -p staticfiles/css
cp staticfiles/styles.css staticfiles/css/styles.css || echo "Error al copiar styles.css a css/"

# Procesar otros archivos CSS importantes
for css_file in vercel.css vercel-fallback.css; do
  if [ -f "static/css/$css_file" ]; then
    echo "Procesando $css_file..."
    cp "static/css/$css_file" "staticfiles/css/$css_file" || echo "Error al copiar $css_file"
    # También lo copiamos a la raíz por si acaso
    cp "static/css/$css_file" "staticfiles/$css_file" || echo "Error al copiar $css_file a raíz"
  else
    echo "ADVERTENCIA: No se encontró static/css/$css_file"
  fi
done

echo "Creando archivo de test para verificar que los estáticos funcionan..."
echo "<html><head><link rel='stylesheet' href='/static/css/styles.css'></head><body><h1>Archivos estáticos funcionando</h1></body></html>" > staticfiles/test.html

echo "Construcción completada"
touch staticfiles/.gitkeep

# Listar archivos para debug
echo "Contenido de staticfiles:"
ls -la staticfiles
echo "Contenido de staticfiles/css:"
ls -la staticfiles/css 2>/dev/null || echo "No existe directorio css"
