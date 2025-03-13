from django.contrib import admin
from django.utils.html import format_html

class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'moneda_preferida', 'foto_perfil_thumbnail', 'recibir_alertas_email')
    list_filter = ('moneda_preferida', 'recibir_alertas_email')
    search_fields = ('usuario__username', 'usuario__email')
    
    # list_display: Campos y métodos mostrados en la lista
    # list_filter: Filtros disponibles
    # search_fields: Permite buscar por usuario o email
    
    def foto_perfil_thumbnail(self, obj):
        """Muestra una miniatura de la foto de perfil si existe"""
        if obj.foto_perfil:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', 
                              obj.foto_perfil.url)
        return "Sin foto"
    
    foto_perfil_thumbnail.short_description = 'Foto'
    
    def get_queryset(self, request):
        """Para usuarios normales, solo muestra su propio perfil"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)
