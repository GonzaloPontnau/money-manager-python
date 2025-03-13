from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .categoria import Categoria

class Presupuesto(models.Model):
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='presupuestos'
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE,
        related_name='presupuestos'
    )
    monto_maximo = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Cantidad máxima a gastar en esta categoría"
    )
    mes = models.IntegerField(
        choices=[(i, i) for i in range(1, 13)],
        help_text="Mes del presupuesto (1-12)"
    )
    año = models.IntegerField(
        help_text="Año del presupuesto"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Presupuesto {self.categoria.nombre} - {self.mes}/{self.año}"
    
    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"
        unique_together = ('usuario', 'categoria', 'mes', 'año')
        ordering = ['-año', '-mes', 'categoria__nombre']
        
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finanzas:detalle_presupuesto', args=[str(self.id)])
        
    def get_gasto_actual(self):
        """Calcula el gasto actual para esta categoría en el mes/año especificado"""
        from django.db.models import Sum
        from .transaccion import Transaccion
        import datetime
        
        primer_dia = datetime.date(self.año, self.mes, 1)
        if self.mes == 12:
            ultimo_dia = datetime.date(self.año + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            ultimo_dia = datetime.date(self.año, self.mes + 1, 1) - datetime.timedelta(days=1)
            
        gasto = Transaccion.objects.filter(
            usuario=self.usuario,
            categoria=self.categoria,
            tipo='gasto',
            fecha__date__gte=primer_dia,
            fecha__date__lte=ultimo_dia
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        return gasto
        
    def get_porcentaje_usado(self):
        """Devuelve el porcentaje del presupuesto que ya se ha gastado"""
        gasto_actual = self.get_gasto_actual()
        if self.monto_maximo > 0:
            return min(100, int((gasto_actual / self.monto_maximo) * 100))
        return 0
        
    @property
    def esta_excedido(self):
        """Indica si el presupuesto se ha excedido"""
        return self.get_gasto_actual() > self.monto_maximo