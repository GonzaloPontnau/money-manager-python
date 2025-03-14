from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from finanzas.models.transaccion import Transaccion

@login_required
def dashboard_view(request):
    """Vista principal del dashboard financiero"""
    # Obtener todas las transacciones del usuario
    transacciones = Transaccion.objects.filter(usuario=request.user).order_by('-fecha')[:10]
    
    # Calcular ingresos totales
    ingresos = Transaccion.objects.filter(
        usuario=request.user, 
        tipo='ingreso'
    ).aggregate(Sum('monto'))['monto__sum'] or 0
    
    # Calcular gastos totales
    gastos = Transaccion.objects.filter(
        usuario=request.user, 
        tipo='gasto'
    ).aggregate(Sum('monto'))['monto__sum'] or 0
    
    # Calcular balance
    balance = ingresos - gastos
    
    context = {
        'transacciones': transacciones,
        'ingresos_totales': ingresos,
        'gastos_totales': gastos,
        'balance': balance,
    }
    
    return render(request, 'finanzas/dashboard.html', context)
