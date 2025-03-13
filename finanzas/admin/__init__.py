from .categoria_admin import CategoriaAdmin
from .transaccion_admin import TransaccionAdmin
from .presupuesto_admin import PresupuestoAdmin
from .perfil_usuario_admin import PerfilUsuarioAdmin
from finanzas.models import Categoria, Transaccion, Presupuesto, PerfilUsuario
from finanzas.admin_site import money_manager_admin

# Registramos con nuestro admin personalizado
money_manager_admin.register(Categoria, CategoriaAdmin)
money_manager_admin.register(Transaccion, TransaccionAdmin)
money_manager_admin.register(Presupuesto, PresupuestoAdmin)
money_manager_admin.register(PerfilUsuario, PerfilUsuarioAdmin)

# También registramos con el admin normal de Django para compatibilidad
from django.contrib import admin
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Transaccion, TransaccionAdmin)
admin.site.register(Presupuesto, PresupuestoAdmin)
admin.site.register(PerfilUsuario, PerfilUsuarioAdmin)
