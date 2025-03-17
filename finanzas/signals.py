from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone

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
        from finanzas.models.categoria import Categoria
        
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

@receiver(post_save, sender=User)
def agregar_monto_inicial(sender, instance, created, **kwargs):
    """
    Agrega un monto inicial de 1000 al registrar un nuevo usuario.
    
    NOTA: Este monto se debe cambiar a 0 en producción. Solo se usa para pruebas.
    """
    if created:
        from finanzas.models.transaccion import Transaccion
        from finanzas.models.categoria import Categoria
        
        # TESTING: Monto inicial para pruebas de 1000
        monto_inicial = 1000
        
        # Buscar una categoría de tipo ingreso para asignar a la transacción
        categoria = Categoria.objects.filter(
            usuario=instance,
            tipo='ingreso'
        ).first()
        
        # Crear la transacción de ingreso inicial
        Transaccion.objects.create(
            usuario=instance,
            monto=monto_inicial,
            tipo='ingreso',
            categoria=categoria,
            descripcion="Monto inicial para pruebas",
            fecha=timezone.now()
        )