from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, authenticate
from .models import Transaccion, Presupuesto
from .forms import RegisterForm

def register(request):
    """Vista para registrar nuevos usuarios"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Iniciar sesión automáticamente después del registro
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, f'¡Cuenta creada con éxito! Bienvenido/a, {user.first_name}.')
            return redirect('finanzas:dashboard')
    else:
        form = RegisterForm()
    return render(request, 'finanzas/register.html', {'form': form})

@login_required
def dashboard(request):
    # Obtener últimas 5 transacciones del usuario
    transacciones = Transaccion.objects.filter(
        usuario=request.user
    ).order_by('-fecha')[:5]
    
    # Cálculo de totales usando agregación de Django
    ingresos = Transaccion.objects.filter(
        usuario=request.user, 
        tipo='ingreso'
    ).aggregate(Sum('monto'))['monto__sum'] or 0  # Default a 0 si no hay resultados
    
    gastos = Transaccion.objects.filter(
        usuario=request.user, 
        tipo='gasto'
    ).aggregate(Sum('monto'))['monto__sum'] or 0
    
    # Datos para gráfico: agrupar gastos por categoría
    categorias_gastos = Transaccion.objects.filter(
        usuario=request.user,
        tipo='gasto'
    ).values('categoria__nombre').annotate(total=Sum('monto'))
    
    # Detección de presupuestos excedidos
    alertas = []
    for presupuesto in Presupuesto.objects.filter(usuario=request.user):
        # Calcular gasto actual para el mes del presupuesto
        gasto_actual = Transaccion.objects.filter(
            categoria=presupuesto.categoria,
            tipo='gasto',
            fecha__month=presupuesto.mes,
            fecha__year=presupuesto.año
        ).aggregate(Sum('monto'))['monto__sum'] or 0
        
        # Lógica de alerta
        if gasto_actual > presupuesto.monto_maximo:
            alertas.append({
                'categoria': presupuesto.categoria.nombre,
                'gasto_actual': gasto_actual,
                'limite': presupuesto.monto_maximo
            })

    # Preparación de datos para template
    context = {
        'ingresos_totales': ingresos,
        'gastos_totales': gastos,
        'balance': ingresos - gastos,
        'transacciones': transacciones,
        'categorias_gastos': list(categorias_gastos),  # Convertir QuerySet a lista
        'alertas': alertas
    }
    return render(request, 'finanzas/dashboard.html', context)