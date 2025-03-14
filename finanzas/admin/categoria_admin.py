from django.contrib import admin
from django.contrib.auth import get_user_model
from finanzas.models import Categoria

Usuario = get_user_model()

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'usuario')
    list_filter = ('tipo', 'usuario')
    search_fields = ('nombre',)
    
    def get_queryset(self, request):
        """Limita las categorías mostradas a las del usuario, excepto para superusuarios"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)
    
    def save_model(self, request, obj, form, change):
        """Asigna automáticamente el usuario actual si no se especifica"""
        if not obj.usuario_id:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limita las opciones de usuario al usuario actual o todos si es superusuario"""
        if db_field.name == 'usuario' and not request.user.is_superuser:
            kwargs["queryset"] = Usuario.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
