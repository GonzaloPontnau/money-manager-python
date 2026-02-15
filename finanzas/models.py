from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


# ── Categoria ───────────────────────────────────────────────────────────────

class Categoria(models.Model):
    TIPO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    ]

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categorias'
    )

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        unique_together = ['nombre', 'usuario']
        ordering = ['tipo', 'nombre']


# ── PerfilUsuario ───────────────────────────────────────────────────────────

class PerfilUsuario(models.Model):
    MONEDAS = [
        ('USD', 'Dólar estadounidense'),
        ('EUR', 'Euro'),
        ('MXN', 'Peso mexicano'),
        ('ARS', 'Peso argentino'),
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

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    def get_balance_actual(self):
        """Calcula el balance actual (ingresos - gastos)."""
        from django.db.models import Sum

        ingresos = Transaccion.objects.filter(
            usuario=self.usuario,
            tipo='ingreso'
        ).aggregate(total=Sum('monto'))['total'] or 0

        gastos = Transaccion.objects.filter(
            usuario=self.usuario,
            tipo='gasto'
        ).aggregate(total=Sum('monto'))['total'] or 0

        return ingresos - gastos


# ── Transaccion ─────────────────────────────────────────────────────────────

class Transaccion(models.Model):
    TIPO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacciones')
    fecha = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, related_name='transacciones'
    )
    descripcion = models.TextField(blank=True, null=True)
    comprobante = models.FileField(
        upload_to='comprobantes/', blank=True, null=True,
        help_text="Recibo o comprobante de la transacción"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"
        ordering = ['-fecha']
        constraints = [
            models.CheckConstraint(
                check=models.Q(monto__gt=0),
                name='transaccion_monto_gt_0',
            ),
        ]

    def __str__(self):
        return f"{self.tipo.capitalize()} - {self.monto} - {self.fecha.strftime('%d/%m/%Y')}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finanzas:detalle_transaccion', args=[str(self.id)])

    @property
    def es_gasto(self):
        return self.tipo == 'gasto'

    @property
    def es_ingreso(self):
        return self.tipo == 'ingreso'


# ── Transferencia ───────────────────────────────────────────────────────────

class Transferencia(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completada'),
        ('failed', 'Fallida'),
        ('cancelled', 'Cancelada'),
    ]

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True,
        help_text="Identificador único para tracking de la transferencia"
    )
    emisor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='transferencias_enviadas'
    )
    receptor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='transferencias_recibidas'
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=255, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    referencia = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="Código de referencia para la transferencia"
    )
    codigo_respuesta = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="Código de respuesta de la API bancaria"
    )
    mensaje_respuesta = models.TextField(
        blank=True, null=True,
        help_text="Mensaje de respuesta de la API bancaria"
    )

    class Meta:
        verbose_name = "Transferencia"
        verbose_name_plural = "Transferencias"
        ordering = ['-fecha_creacion']
        constraints = [
            models.CheckConstraint(
                check=models.Q(monto__gt=0),
                name='transferencia_monto_gt_0',
            ),
            models.CheckConstraint(
                check=~models.Q(emisor=models.F('receptor')),
                name='transferencia_emisor_receptor_diferentes',
            ),
        ]

    def __str__(self):
        return f"Transferencia {self.uuid}: {self.emisor.username} → {self.receptor.username} ({self.monto})"

    def save(self, *args, **kwargs):
        if not self.referencia:
            self.referencia = f"TR-{str(self.uuid)[:8].upper()}"
        super().save(*args, **kwargs)

    def completar(self):
        """Marca la transferencia como completada y registra la fecha."""
        self.estado = 'completed'
        self.fecha_procesamiento = timezone.now()
        self.save()

    def fallar(self, mensaje=None):
        """Marca la transferencia como fallida."""
        self.estado = 'failed'
        if mensaje:
            self.mensaje_respuesta = mensaje
        self.fecha_procesamiento = timezone.now()
        self.save()

    def cancelar(self):
        """Cancela la transferencia (solo si está pendiente)."""
        if self.estado == 'pending':
            self.estado = 'cancelled'
            self.fecha_procesamiento = timezone.now()
            self.save()
            return True
        return False


# ── Presupuesto ─────────────────────────────────────────────────────────────

class Presupuesto(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='presupuestos'
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name='presupuestos'
    )
    monto_maximo = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Cantidad máxima a gastar en esta categoría"
    )
    mes = models.IntegerField(
        choices=[(i, i) for i in range(1, 13)],
        help_text="Mes del presupuesto (1-12)"
    )
    año = models.IntegerField(help_text="Año del presupuesto")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"
        unique_together = ('usuario', 'categoria', 'mes', 'año')
        ordering = ['-año', '-mes', 'categoria__nombre']

    def __str__(self):
        return f"Presupuesto {self.categoria.nombre} - {self.mes}/{self.año}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finanzas:detalle_presupuesto', args=[str(self.id)])

    def get_gasto_actual(self):
        """Calcula el gasto actual para esta categoría en el mes/año especificado."""
        import datetime
        from django.db.models import Sum

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
        """Devuelve el porcentaje del presupuesto que ya se ha gastado."""
        gasto_actual = self.get_gasto_actual()
        if self.monto_maximo > 0:
            return min(100, int((gasto_actual / self.monto_maximo) * 100))
        return 0

    @property
    def esta_excedido(self):
        """Indica si el presupuesto se ha excedido."""
        return self.get_gasto_actual() > self.monto_maximo
