from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class CachingMiddleware(MiddlewareMixin):
    """Middleware que agrega encabezados de caché para mejorar el rendimiento."""
    
    def process_response(self, request, response):
        # No cachear si es una petición de administrador o autenticación
        if request.path.startswith('/admin/') or request.path.startswith('/login/'):
            return response
        
        # Cachear recursos estáticos por más tiempo
        if 'static' in request.path:
            response['Cache-Control'] = 'public, max-age=31536000'  # 1 año
            return response
            
        # Cachear respuestas normales por un tiempo moderado
        if request.method == 'GET' and response.status_code == 200:
            response['Cache-Control'] = 'public, max-age=300'  # 5 minutos
            
        return response
