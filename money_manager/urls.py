"""
URL configuration for money_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection

# Vista simple para verificar el estado de la base de datos
def db_status(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        db_info = {
            "status": "ok" if result and result[0] == 1 else "error",
            "message": "Base de datos conectada correctamente",
            "engine": connection.vendor,
        }
    except Exception as e:
        db_info = {
            "status": "error",
            "message": str(e),
            "engine": getattr(connection, 'vendor', 'unknown'),
        }
    
    return JsonResponse(db_info)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('finanzas.urls')),
    path('db-status/', db_status, name='db_status'),  # URL para verificar la conexión a la BD
]

# Configuración para servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Añadimos configuración para producción (incluido Vercel)
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
