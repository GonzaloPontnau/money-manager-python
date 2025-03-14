from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Eliminamos la importación del modelo PerfilUsuario ya que fue eliminado
# Anteriormente: from .models import PerfilUsuario

# Puedes añadir otras señales que no dependan de PerfilUsuario
# Por ejemplo, para crear categorías por defecto al crear un usuario:

@receiver(post_save, sender=User)
def crear_categorias_por_defecto(sender, instance, created, **kwargs):
    """
    Crea categorías por defecto cuando se registra un nuevo usuario.
    """
    if created:
        from finanzas.models import Categoria
        
        # Categorías de ingreso por defecto
        categorias_ingreso = ["Salario", "Transferencia recibida", "Otro ingreso"]
        for nombre in categorias_ingreso:
            Categoria.objects.create(
                nombre=nombre,
                tipo='ingreso',
                usuario=instance
            )
        
        # Categorías de gasto por defecto
        categorias_gasto = ["Transferencia enviada", "Compras", "Otro gasto"]
        for nombre in categorias_gasto:
            Categoria.objects.create(
                nombre=nombre,
                tipo='gasto',
                usuario=instance
            )