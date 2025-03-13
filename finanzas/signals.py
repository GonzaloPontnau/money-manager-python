from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea un perfil de usuario automáticamente cuando se crea un usuario"""
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Guarda el perfil de usuario cuando se actualiza el usuario"""
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
    else:
        # Por si acaso el perfil no existe
        PerfilUsuario.objects.create(usuario=instance) 