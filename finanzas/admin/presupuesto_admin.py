from django.contrib import admin
from django.utils.html import format_html

class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'mes_año', 'monto_maximo', 'gasto_actual', 'porcentaje_usado_display')
    list_filter = ('mes', 'año', 'usuario', 'categoria')
    search_fields = ('categoria__nombre',)
    ordering = ('-año', '-mes', 'categoria__nombre')
    
    # list_display: Campos mostrados en la lista, incluyendo métodos personalizados
    # list_filter: Permite filtrar por estos campos
    # search_fields: Permite buscar por nombre de categoría
    # ordering: Define el orden por defecto
    
    def mes_año(self, obj):
        """Muestra mes/año en formato legible"""
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return f"{meses[obj.mes-1]} {obj.año}"
    
    mes_año.short_description = 'Período'
    
    def gasto_actual(self, obj):
        """Muestra el gasto actual de la categoría en el período"""
        return obj.get_gasto_actual()
    
    gasto_actual.short_description = 'Gasto Actual'
    
    def porcentaje_usado_display(self, obj):
        """Muestra una barra de progreso con el porcentaje usado del presupuesto"""
        porcentaje = obj.get_porcentaje_usado()
        color = 'green'
        if porcentaje > 80:
            color = 'orange'
        if porcentaje > 100:
            color = 'red'
            
        return format_html(
            '<div style="width:100px; border:1px solid #ccc;">'
            '<div style="width:{}px; height:20px; background-color:{};">&nbsp;</div>'
            '</div> {}%',
            min(100, porcentaje), color, porcentaje
        )
    
    porcentaje_usado_display.short_description = 'Usado'
    
    def get_queryset(self, request):
        """Limita los presupuestos mostrados a los del usuario, excepto para superusuarios"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)
        
    def save_model(self, request, obj, form, change):
        """Asigna automáticamente el usuario actual si no se especifica"""
        if not obj.usuario_id:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)
