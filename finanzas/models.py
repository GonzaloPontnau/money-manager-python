














# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Modelo de usuario personalizado heredando de AbstractUser
class Usuario(AbstractUser):
    # Campo adicional para selección de moneda con opciones predefinidas
    MONEDAS = [
        ('USD', 'Dólar estadounidense'),
        ('EUR', 'Euro'),
        ('MXN', 'Peso mexicano'),
        ('ARS', 'Peso argentino')
    ]
    moneda_preferida = models.CharField(
        max_length=3, 
        choices=MONEDAS, 
        default='ARS'
    )

# Modelo para categorías de transacciones con límite opcional
class Categoria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Relación 1:N con usuario
    nombre = models.CharField(max_length=50)  # Nombre de la categoría
    limite = models.DecimalField(  # Límite de gasto opcional
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.nombre

# Modelo principal para registrar transacciones financieras
class Transaccion(models.Model):
    TIPOS = [  # Opciones para tipo de transacción
        ('ING', 'Ingreso'),
        ('GAS', 'Gasto'),
    ]
    
    # Relaciones y campos básicos
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)  # Fecha automática actual por defecto
    monto = models.DecimalField(max_digits=12, decimal_places=2)  # Valor numérico preciso
    tipo = models.CharField(max_length=3, choices=TIPOS)  # Selección de tipo
    categoria = models.ForeignKey(  # Categoría opcional (puede ser null)
        Categoria, 
        on_delete=models.SET_NULL, 
        null=True
    )
    descripcion = models.TextField(blank=True)  # Campo de texto opcional

    class Meta:
        ordering = ['-fecha']  # Orden por defecto: más reciente primero

# Modelo para definir presupuestos mensuales por categoría
class Presupuesto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    mes = models.DateField(default=timezone.now)  # Fecha para determinar el mes/año
    monto_maximo = models.DecimalField(max_digits=12, decimal_places=2)  # Límite presupuestario

    def __str__(self):
        return f"{self.categoria.nombre} - {self.mes:%B %Y}"