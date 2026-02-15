from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_save, sender=User)
def crear_categorias_por_defecto(sender, instance, created, **kwargs):
    """Crea categorÃ­as por defecto al registrar un usuario."""
    if not created:
        return

    from finanzas.models import Categoria

    for nombre in ["Salario", "Transferencia recibida", "Otro ingreso"]:
        Categoria.objects.get_or_create(
            nombre=nombre,
            tipo="ingreso",
            usuario=instance,
        )

    for nombre in ["Transferencia enviada", "Compras", "Otro gasto"]:
        Categoria.objects.get_or_create(
            nombre=nombre,
            tipo="gasto",
            usuario=instance,
        )


@receiver(post_save, sender=User)
def agregar_monto_inicial(sender, instance, created, **kwargs):
    """Crea un saldo inicial solo si se habilita explÃ­citamente en desarrollo."""
    if not created:
        return

    if not settings.ENABLE_DEV_SEED_DATA:
        return

    monto_inicial = settings.SEED_INITIAL_BALANCE
    if monto_inicial <= 0:
        return

    from finanzas.models import Categoria, Transaccion

    categoria = Categoria.objects.filter(
        usuario=instance,
        tipo="ingreso",
        nombre="Salario",
    ).first() or Categoria.objects.filter(usuario=instance, tipo="ingreso").first()

    Transaccion.objects.create(
        usuario=instance,
        monto=monto_inicial,
        tipo="ingreso",
        categoria=categoria,
        descripcion="Saldo inicial de desarrollo",
        fecha=timezone.now(),
    )

