#!/usr/bin/env python
"""
Script para agregar un monto inicial a todos los usuarios existentes.
Ejecutar con: python manage.py shell < agregar_saldo_usuarios.py
"""

import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'money_manager.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from finanzas.models.transaccion import Transaccion
from finanzas.models.categoria import Categoria

def agregar_saldo_inicial():
    """
    Agrega un saldo inicial de 1000 a todos los usuarios existentes
    que no tengan transacciones o cuyo saldo sea menor a 100.
    
    NOTA: Este script es solo para propósitos de prueba.
    """
    # TESTING: Monto inicial para pruebas
    monto_inicial = 1000
    
    # Procesar todos los usuarios
    usuarios = User.objects.all()
    contador = 0
    
    for usuario in usuarios:
        # Calcular saldo actual
        ingresos = Transaccion.objects.filter(
            usuario=usuario, 
            tipo='ingreso'
        ).aggregate(Sum('monto'))['monto__sum'] or 0
        
        gastos = Transaccion.objects.filter(
            usuario=usuario, 
            tipo='gasto'
        ).aggregate(Sum('monto'))['monto__sum'] or 0
        
        saldo_actual = ingresos - gastos
        
        # Solo agregar saldo si el usuario tiene menos de 100
        if saldo_actual < 100:
            # Buscar una categoría de tipo ingreso
            categoria = Categoria.objects.filter(
                usuario=usuario,
                tipo='ingreso'
            ).first()
            
            # Si no hay categoría, crear una
            if not categoria:
                categoria = Categoria.objects.create(
                    nombre="Salario",
                    tipo='ingreso',
                    usuario=usuario
                )
            
            # Crear la transacción de ingreso
            Transaccion.objects.create(
                usuario=usuario,
                monto=monto_inicial,
                tipo='ingreso',
                categoria=categoria,
                descripcion="Monto inicial para pruebas (script)",
                fecha=timezone.now()
            )
            
            contador += 1
            print(f"Saldo agregado a {usuario.username}")
    
    print(f"\nSe agregó saldo a {contador} usuarios de {usuarios.count()} totales.")
    print("NOTA: Este saldo es solo para pruebas y debe ser eliminado en producción.")

if __name__ == "__main__":
    agregar_saldo_inicial() 