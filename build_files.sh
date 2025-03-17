# Script para crear archivos estáticos y ejecutar migraciones
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
chmod +x build_files.sh  # Esta línea se ejecuta en Vercel
