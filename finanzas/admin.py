from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils.html import format_html

from finanzas.models import Categoria, Transaccion, Transferencia, PerfilUsuario, Presupuesto

Usuario = get_user_model()


# ── Categoria ───────────────────────────────────────────────────────────────

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'usuario')
    list_filter = ('tipo', 'usuario')
    search_fields = ('nombre',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.usuario_id:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'usuario' and not request.user.is_superuser:
            kwargs["queryset"] = Usuario.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ── Transaccion ─────────────────────────────────────────────────────────────

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'descripcion', 'monto_display', 'tipo', 'categoria')
    list_filter = ('tipo', 'fecha', 'categoria', 'usuario')
    search_fields = ('descripcion',)
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    fieldsets = (
        ('Información básica', {
            'fields': ('usuario', 'fecha', 'monto', 'tipo')
        }),
        ('Categorización', {
            'fields': ('categoria', 'descripcion')
        }),
        ('Documentación', {
            'fields': ('comprobante',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    def monto_display(self, obj):
        color = 'green' if obj.tipo == 'ingreso' else 'red'
        prefix = '+' if obj.tipo == 'ingreso' else '-'
        return format_html('<span style="color: {};">{} {}</span>',
                          color, prefix, obj.monto)
    monto_display.short_description = 'Monto'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.usuario_id:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        if hasattr(response, 'context_data'):
            qs = response.context_data['cl'].queryset
            total_ingresos = qs.filter(tipo='ingreso').aggregate(Sum('monto'))['monto__sum'] or 0
            total_gastos = qs.filter(tipo='gasto').aggregate(Sum('monto'))['monto__sum'] or 0
            response.context_data['total_ingresos'] = total_ingresos
            response.context_data['total_gastos'] = total_gastos
            response.context_data['balance'] = total_ingresos - total_gastos

        return response


# ── Transferencia ───────────────────────────────────────────────────────────

@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'emisor', 'receptor', 'monto', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('emisor__username', 'receptor__username', 'concepto')
    readonly_fields = ('uuid', 'referencia', 'fecha_creacion', 'fecha_procesamiento')


# ── PerfilUsuario ───────────────────────────────────────────────────────────

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'moneda_preferida', 'foto_perfil_thumbnail', 'recibir_alertas_email')
    list_filter = ('moneda_preferida', 'recibir_alertas_email')
    search_fields = ('usuario__username', 'usuario__email')

    def foto_perfil_thumbnail(self, obj):
        if obj.foto_perfil:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />',
                              obj.foto_perfil.url)
        return "Sin foto"
    foto_perfil_thumbnail.short_description = 'Foto'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)


# ── Presupuesto ─────────────────────────────────────────────────────────────

@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'mes_año', 'monto_maximo', 'gasto_actual', 'porcentaje_usado_display')
    list_filter = ('mes', 'año', 'usuario', 'categoria')
    search_fields = ('categoria__nombre',)
    ordering = ('-año', '-mes', 'categoria__nombre')

    def mes_año(self, obj):
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return f"{meses[obj.mes-1]} {obj.año}"
    mes_año.short_description = 'Período'

    def gasto_actual(self, obj):
        return obj.get_gasto_actual()
    gasto_actual.short_description = 'Gasto Actual'

    def porcentaje_usado_display(self, obj):
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
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.usuario_id:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)
