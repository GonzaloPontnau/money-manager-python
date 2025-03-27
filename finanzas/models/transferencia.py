from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Transferencia(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completada'),
        ('failed', 'Fallida'),
        ('cancelled', 'Cancelada'),
    ]
    
    # Identificador único para cada transferencia
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, help_text="Identificador único para tracking de la transferencia")    
    
    # Campos de usuario (emisor y receptor)
    emisor = models.ForeignKey( User,  on_delete=models.CASCADE, related_name='transferencias_enviadas')
    receptor = models.ForeignKey( User,  on_delete=models.CASCADE, related_name='transferencias_recibidas')
    
    # Detalles de la transferencia
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=255, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    
    # Estado y tracking
    estado = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    referencia = models.CharField(max_length=50, blank=True, null=True, help_text="Código de referencia para la transferencia")
    
    # Para posible integración con API bancaria
    codigo_respuesta = models.CharField(max_length=50, blank=True, null=True, help_text="Código de respuesta de la API bancaria")
    mensaje_respuesta = models.TextField(blank=True, null=True, help_text="Mensaje de respuesta de la API bancaria")
    
    class Meta:
        verbose_name = "Transferencia"
        verbose_name_plural = "Transferencias"
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return f"Transferencia {self.uuid}: {self.emisor.username} → {self.receptor.username} ({self.monto})"
    
    def save(self, *args, **kwargs):
        # Generamos una referencia para la transferencia si no tiene una
        if not self.referencia:
            self.referencia = f"TR-{str(self.uuid)[:8].upper()}"
        super().save(*args, **kwargs)
    
    def completar(self):
        """Marca la transferencia como completada y registra la fecha"""
        self.estado = 'completed'
        self.fecha_procesamiento = timezone.now()
        self.save()
        
    def fallar(self, mensaje=None):
        """Marca la transferencia como fallida"""
        self.estado = 'failed'
        if mensaje:
            self.mensaje_respuesta = mensaje
        self.fecha_procesamiento = timezone.now()
        self.save()
    
    def cancelar(self):
        """Cancela la transferencia (solo si está pendiente)"""
        if self.estado == 'pending':
            self.estado = 'cancelled'
            self.fecha_procesamiento = timezone.now()
            self.save()
            return True
        return False
