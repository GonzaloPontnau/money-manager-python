#!/bin/bash
# Script para crear archivos estáticos y ejecutar migraciones

# Detectar el comando Python disponible
if command -v python3.12 &> /dev/null; then
	PYTHON_CMD="python3.12"
elif command -v python3 &> /dev/null; then
	PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
	PYTHON_CMD="python"
else
	echo "Error: No se encontró Python. Por favor, instale Python 3."
	exit 1
fi

echo "Usando $PYTHON_CMD para la instalación"
echo "Instalando dependencias..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt

echo "Creando directorio de estáticos..."
mkdir -p staticfiles

echo "Recogiendo archivos estáticos..."
$PYTHON_CMD manage.py collectstatic --noinput

echo "Ejecutando migraciones..."
$PYTHON_CMD manage.py migrate

echo "Construcción completada"
touch staticfiles/.gitkeep
