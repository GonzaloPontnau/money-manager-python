from django.urls import path
from finanzas.views.dashboard_views import dashboard_view
from finanzas.views.auth_views import login_view, register_view, logout_view
from finanzas.views.transferencia_views import (
    lista_transferencias, 
    nueva_transferencia,
    detalle_transferencia,
    cancelar_transferencia
)
from finanzas.views.transaccion_views import (
    lista_transacciones,
    nueva_transaccion,
    editar_transaccion,
    eliminar_transaccion,
    detalle_transaccion,
    filtrar_categorias
)

app_name = 'finanzas'

urlpatterns = [
    # Vistas de autenticación
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    
    # Dashboard principal
    path('', dashboard_view, name='dashboard'),
    
    # Transferencias
    path('transferencias/', lista_transferencias, name='lista_transferencias'),
    path('transferencias/nueva/', nueva_transferencia, name='nueva_transferencia'),
    path('transferencias/<uuid:uuid>/', detalle_transferencia, name='detalle_transferencia'),
    path('transferencias/<uuid:uuid>/cancelar/', cancelar_transferencia, name='cancelar_transferencia'),
    
    # Transacciones
    path('transacciones/', lista_transacciones, name='lista_transacciones'),
    path('transacciones/nueva/', nueva_transaccion, name='nueva_transaccion'),
    path('transacciones/<int:id>/', detalle_transaccion, name='detalle_transaccion'),
    path('transacciones/<int:id>/editar/', editar_transaccion, name='editar_transaccion'),
    path('transacciones/<int:id>/eliminar/', eliminar_transaccion, name='eliminar_transaccion'),
    path('api/categorias-por-tipo/', filtrar_categorias, name='filtrar_categorias'),
]