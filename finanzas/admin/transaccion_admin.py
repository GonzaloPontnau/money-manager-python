from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum

class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'descripcion', 'monto_display', 'tipo', 'categoria')
    list_filter = ('tipo', 'fecha', 'categoria', 'usuario')
    search_fields = ('descripcion',)
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    # list_display: Muestra estos campos en la lista
    # list_filter: Permite filtrar por estos campos
    # search_fields: Permite buscar en estos campos
    # date_hierarchy: Crea filtros jerárquicos por fecha
    # readonly_fields: Campos que no se pueden editar
    
    fieldsets = (
        ('Información básica', {
            'fields': ('usuario', 'fecha', 'monto', 'tipo')
        }),
        ('Categorización', {
            'fields': ('categoria', 'descripcion')
        }),
        ('Documentación', {
            'fields': ('comprobante',),
            'classes': ('collapse',)  # Sección colapsable
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    # Los fieldsets dividen el formulario en secciones para mejor organización
    
    def monto_display(self, obj):
        """Colorea el monto según sea ingreso (verde) o gasto (rojo)"""
        color = 'green' if obj.tipo == 'ingreso' else 'red'
        prefix = '+' if obj.tipo == 'ingreso' else '-'
        return format_html('<span style="color: {};">{} {}</span>', 
                          color, prefix, obj.monto)
    
    monto_display.short_description = 'Monto'
    
    def get_queryset(self, request):
        """Limita las transacciones mostradas a las del usuario, excepto para superusuarios"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)
        
    def save_model(self, request, obj, form, change):
        """Asigna automáticamente el usuario actual si no se especifica"""
        if not obj.usuario_id:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)
        
    def changelist_view(self, request, extra_context=None):
        """Añade resumen de totales al pie de la lista"""
        response = super().changelist_view(request, extra_context)
        
        # Si la página se está renderizando y no es una respuesta HttpResponseRedirect
        if hasattr(response, 'context_data'):
            qs = response.context_data['cl'].queryset
            
            # Calculamos totales de ingresos y gastos
            total_ingresos = qs.filter(tipo='ingreso').aggregate(Sum('monto'))['monto__sum'] or 0
            total_gastos = qs.filter(tipo='gasto').aggregate(Sum('monto'))['monto__sum'] or 0
            
            # Añadimos al contexto
            response.context_data['total_ingresos'] = total_ingresos
            response.context_data['total_gastos'] = total_gastos
            response.context_data['balance'] = total_ingresos - total_gastos
            
        return response
