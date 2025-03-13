from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    limite = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Límite mensual para esta categoría (opcional)"
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='categorias'
    )
    
    # Para íconos opcionales si quieres añadirlos en el futuro
    icono = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=7, default="#0099ff")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
        unique_together = ['nombre', 'usuario']  # Evita categorías duplicadas por usuario