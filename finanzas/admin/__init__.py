from .categoria_admin import CategoriaAdmin
from .transaccion_admin import TransaccionAdmin
from finanzas.models import Categoria, Transaccion, Transferencia

# Registramos con el admin de Django
from django.contrib import admin
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Transaccion, TransaccionAdmin)
admin.site.register(Transferencia) # Registramos Transferencia con el AdminModel por defecto
