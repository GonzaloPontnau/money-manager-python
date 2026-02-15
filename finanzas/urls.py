from django.urls import path
from finanzas.views import (
    login_view, register_view, logout_view,
    dashboard_view, dashboard_data_api, cargar_datos_demo,
    demo_view, demo_data_api,
    lista_transacciones, nueva_transaccion, editar_transaccion,
    eliminar_transaccion, detalle_transaccion, filtrar_categorias,
    lista_transferencias, nueva_transferencia,
    detalle_transferencia, cancelar_transferencia,
)

app_name = 'finanzas'

urlpatterns = [
    # Autenticación
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    # Dashboard
    path('', dashboard_view, name='dashboard'),
    path('demo/', demo_view, name='demo'),
    path('api/dashboard-data/', dashboard_data_api, name='dashboard_data_api'),
    path('api/demo-data/', demo_data_api, name='demo_data_api'),
    path('dashboard/cargar-demo/', cargar_datos_demo, name='cargar_datos_demo'),

    # Transacciones
    path('transacciones/', lista_transacciones, name='lista_transacciones'),
    path('transacciones/nueva/', nueva_transaccion, name='nueva_transaccion'),
    path('transacciones/<int:id>/', detalle_transaccion, name='detalle_transaccion'),
    path('transacciones/<int:id>/editar/', editar_transaccion, name='editar_transaccion'),
    path('transacciones/<int:id>/eliminar/', eliminar_transaccion, name='eliminar_transaccion'),
    path('api/categorias-por-tipo/', filtrar_categorias, name='filtrar_categorias'),

    # Transferencias
    path('transferencias/', lista_transferencias, name='lista_transferencias'),
    path('transferencias/nueva/', nueva_transferencia, name='nueva_transferencia'),
    path('transferencias/<uuid:uuid>/', detalle_transferencia, name='detalle_transferencia'),
    path('transferencias/<uuid:uuid>/cancelar/', cancelar_transferencia, name='cancelar_transferencia'),
]
