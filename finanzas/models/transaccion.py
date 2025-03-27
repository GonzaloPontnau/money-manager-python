from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .categoria import Categoria

class Transaccion(models.Model):
    TIPO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacciones')
    fecha = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='transacciones')
    descripcion = models.TextField(blank=True, null=True)
    
    # Campos adicionales útiles
    comprobante = models.FileField( upload_to='comprobantes/',  blank=True,  null=True, help_text="Recibo o comprobante de la transacción")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.tipo.capitalize()} - {self.monto} - {self.fecha.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"
        ordering = ['-fecha']
        
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finanzas:detalle_transaccion', args=[str(self.id)])
        
    @property
    def es_gasto(self):
        return self.tipo == 'gasto'
        
    @property
    def es_ingreso(self):
        return self.tipo == 'ingreso'