import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils.timezone import now, timedelta
from django.views.decorators.cache import cache_page

from finanzas.models.transaccion import Transaccion

logger = logging.getLogger(__name__)

@login_required
def dashboard_view(request):
    """Vista del dashboard principal"""
    # Optimizar consultas para obtener resúmenes en una sola operación
    totales = Transaccion.objects.filter(
        usuario=request.user
    ).values('tipo').annotate(
        total=Sum('monto')
    ).order_by('tipo')
    
    ingresos_totales = 0
    gastos_totales = 0
    for item in totales:
        if item['tipo'] == 'ingreso':
            ingresos_totales = item['total'] or 0
        elif item['tipo'] == 'gasto':
            gastos_totales = item['total'] or 0
    
    # Limitar transacciones recientes a un número pequeño y optimizar con select_related
    transacciones = Transaccion.objects.filter(
        usuario=request.user
    ).select_related('categoria').order_by('-fecha')[:5]
    
    context = {
        'ingresos_totales': ingresos_totales,
        'gastos_totales': gastos_totales,
        'balance': ingresos_totales - gastos_totales,
        'transacciones': transacciones,
    }
    
    return render(request, 'finanzas/dashboard.html', context)
