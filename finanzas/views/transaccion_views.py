from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.urls import reverse

from finanzas.models.transaccion import Transaccion
from finanzas.models.categoria import Categoria
from finanzas.forms.transaccion_form import TransaccionForm

@login_required
def lista_transacciones(request):
    """Vista para mostrar un listado de transacciones del usuario"""
    # Filtrar según el tipo de transacción (si se especifica)
    tipo = request.GET.get('tipo')
    categoria_id = request.GET.get('categoria')
    
    # Iniciar con todas las transacciones del usuario
    transacciones = Transaccion.objects.filter(usuario=request.user)
    
    # Aplicar filtros si están presentes
    if tipo and tipo in dict(Transaccion.TIPO_CHOICES):
        transacciones = transacciones.filter(tipo=tipo)
    
    if categoria_id:
        transacciones = transacciones.filter(categoria_id=categoria_id)
    
    # Ordenar por fecha descendente
    transacciones = transacciones.order_by('-fecha')
    
    # Obtener categorías del usuario para el filtro
    categorias = Categoria.objects.filter(usuario=request.user)
    
    # Calcular totales
    ingresos = Transaccion.objects.filter(
        usuario=request.user, 
        tipo='ingreso'
    ).aggregate(Sum('monto'))['monto__sum'] or 0
    
    gastos = Transaccion.objects.filter(
        usuario=request.user, 
        tipo='gasto'
    ).aggregate(Sum('monto'))['monto__sum'] or 0
    
    context = {
        'transacciones': transacciones,
        'categorias': categorias,
        'tipo_seleccionado': tipo,
        'categoria_seleccionada': categoria_id,
        'ingresos_totales': ingresos,
        'gastos_totales': gastos,
        'balance': ingresos - gastos,
    }
    
    return render(request, 'finanzas/transacciones/lista.html', context)

@login_required
def nueva_transaccion(request):
    """Vista para crear una nueva transacción"""
    if request.method == 'POST':
        form = TransaccionForm(request.POST, request.FILES, usuario=request.user)
        if form.is_valid():
            transaccion = form.save()
            messages.success(request, "Transacción registrada correctamente")
            
            # Redirigir a la lista o a otra nueva transacción según el botón usado
            if 'guardar_continuar' in request.POST:
                return redirect('finanzas:nueva_transaccion')
            else:
                return redirect('finanzas:lista_transacciones')
    else:
        # Preseleccionar tipo si viene en el querystring
        tipo_inicial = request.GET.get('tipo', '')
        if tipo_inicial:
            form = TransaccionForm(usuario=request.user, initial={'tipo': tipo_inicial})
        else:
            form = TransaccionForm(usuario=request.user)
    
    context = {
        'form': form,
        'title': 'Nueva Transacción',
    }
    
    return render(request, 'finanzas/transacciones/formulario.html', context)

@login_required
def editar_transaccion(request, id):
    """Vista para editar una transacción existente"""
    transaccion = get_object_or_404(Transaccion, id=id, usuario=request.user)
    
    if request.method == 'POST':
        form = TransaccionForm(request.POST, request.FILES, usuario=request.user, instance=transaccion)
        if form.is_valid():
            form.save()
            messages.success(request, "Transacción actualizada correctamente")
            return redirect('finanzas:lista_transacciones')
    else:
        form = TransaccionForm(usuario=request.user, instance=transaccion)
    
    context = {
        'form': form,
        'title': 'Editar Transacción',
        'transaccion': transaccion,
    }
    
    return render(request, 'finanzas/transacciones/formulario.html', context)

@login_required
def eliminar_transaccion(request, id):
    """Vista para eliminar una transacción"""
    transaccion = get_object_or_404(Transaccion, id=id, usuario=request.user)
    
    if request.method == 'POST':
        transaccion.delete()
        messages.success(request, "Transacción eliminada correctamente")
        return redirect('finanzas:lista_transacciones')
    
    context = {
        'transaccion': transaccion,
    }
    
    return render(request, 'finanzas/transacciones/confirmar_eliminar.html', context)

@login_required
def detalle_transaccion(request, id):
    """Vista para ver detalles de una transacción específica"""
    transaccion = get_object_or_404(Transaccion, id=id, usuario=request.user)
    
    context = {
        'transaccion': transaccion,
    }
    
    return render(request, 'finanzas/transacciones/detalle.html', context)

@login_required
def filtrar_categorias(request):
    """Vista AJAX para filtrar categorías según el tipo seleccionado"""
    tipo = request.GET.get('tipo', '')
    categorias = []
    
    if tipo in dict(Transaccion.TIPO_CHOICES):
        categorias = list(Categoria.objects.filter(
            usuario=request.user,
            tipo=tipo
        ).values('id', 'nombre'))
    
    return JsonResponse({'categorias': categorias}) 