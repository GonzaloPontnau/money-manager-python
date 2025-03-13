from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    MONEDAS = [
        ('USD', 'Dólar estadounidense'),
        ('EUR', 'Euro'),
        ('MXN', 'Peso mexicano'),
        ('ARS', 'Peso argentino')
        # se pueden agregar mas
    ]
    
    usuario = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    moneda_preferida = models.CharField(
        max_length=3, 
        choices=MONEDAS, 
        default='USD',
        help_text="Moneda en la que se mostrarán los valores por defecto"
    )
    
    # Campos adicionales que podrían ser útiles
    foto_perfil = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )
    recibir_alertas_email = models.BooleanField(
        default=True,
        help_text="Recibir alertas por correo cuando se excedan los presupuestos"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
        
    def get_balance_actual(self):
        """Calcula el balance actual (ingresos - gastos)"""
        from django.db.models import Sum, Q
        from .transaccion import Transaccion
        
        ingresos = Transaccion.objects.filter(
            usuario=self.usuario, 
            tipo='ingreso'
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        gastos = Transaccion.objects.filter(
            usuario=self.usuario, 
            tipo='gasto'
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        return ingresos - gastos