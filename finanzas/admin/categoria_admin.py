from django.contrib import admin

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'limite', 'color')
    list_filter = ('usuario',)
    search_fields = ('nombre',)
    list_editable = ('color', 'limite')
    
    # list_display: Determina qué campos se muestran en la lista de categorías
    # list_filter: Permite filtrar categorías por usuario (PK)
    # search_fields: Permite buscar categorías por nombre
    # list_editable: Permite editar color y límite directamente desde la lista
    
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
