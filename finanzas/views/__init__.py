# Este archivo está vacío, simplemente marca el directorio como un paquete Python

from finanzas.views.auth_views import login_view, register_view, logout_view
from finanzas.views.dashboard_views import dashboard_view
from finanzas.views.transferencia_views import lista_transferencias, nueva_transferencia, detalle_transferencia, cancelar_transferencia
from finanzas.views.transaccion_views import lista_transacciones, nueva_transaccion, editar_transaccion, eliminar_transaccion, detalle_transaccion, filtrar_categorias

__all__ = [
    'login_view', 'register_view', 'logout_view',
    'dashboard_view',
    'lista_transferencias', 'nueva_transferencia', 'detalle_transferencia', 'cancelar_transferencia',
    'lista_transacciones', 'nueva_transaccion', 'editar_transaccion', 'eliminar_transaccion', 
    'detalle_transaccion', 'filtrar_categorias',
]
