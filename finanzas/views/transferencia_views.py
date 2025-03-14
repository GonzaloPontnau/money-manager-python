from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

from finanzas.models.transferencia import Transferencia
from finanzas.models.transaccion import Transaccion
from finanzas.forms.transferencia_form import TransferenciaForm

@login_required
def lista_transferencias(request):
    """Vista para mostrar un listado de transferencias del usuario"""
    # Obtener todas las transferencias donde el usuario es emisor o receptor
    transferencias = Transferencia.objects.filter(
        Q(emisor=request.user) | Q(receptor=request.user)
    ).order_by('-fecha_creacion')
    
    # Separar transferencias enviadas y recibidas
    enviadas = transferencias.filter(emisor=request.user)
    recibidas = transferencias.filter(receptor=request.user)
    
    context = {
        'transferencias': transferencias,
        'enviadas': enviadas,
        'recibidas': recibidas,
    }
    
    return render(request, 'finanzas/transferencias/lista.html', context)

@login_required
def nueva_transferencia(request):
    """Vista para crear una nueva transferencia entre usuarios"""
    if request.method == 'POST':
        form = TransferenciaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Crear la transferencia pero sin guardarla aún
                    transferencia = form.save(commit=False)
                    transferencia.emisor = request.user
                    
                    # Validar que el usuario tenga saldo suficiente
                    saldo_actual = calcular_saldo_usuario(request.user)
                    
                    if saldo_actual < transferencia.monto:
                        messages.error(request, f"No tienes saldo suficiente. Tu saldo actual es: {saldo_actual}")
                        return render(request, 'finanzas/transferencias/nueva.html', {'form': form})
                    
                    # Guardar la transferencia
                    transferencia.save()
                    
                    # Crear transacciones asociadas
                    # 1. Gasto para el emisor
                    Transaccion.objects.create(
                        usuario=request.user,
                        fecha=timezone.now(),
                        monto=transferencia.monto,
                        tipo='gasto',
                        descripcion=f"Transferencia a {transferencia.receptor.username}: {transferencia.concepto}"
                    )
                    
                    # 2. Ingreso para el receptor
                    Transaccion.objects.create(
                        usuario=transferencia.receptor,
                        fecha=timezone.now(),
                        monto=transferencia.monto,
                        tipo='ingreso',
                        descripcion=f"Transferencia de {request.user.username}: {transferencia.concepto}"
                    )
                    
                    # Marcar la transferencia como completada
                    transferencia.completar()
                    
                    messages.success(request, f"Transferencia de {transferencia.monto} realizada con éxito a {transferencia.receptor.username}")
                    return redirect('finanzas:lista_transferencias')
                    
            except Exception as e:
                messages.error(request, f"Error al realizar la transferencia: {str(e)}")
    else:
        form = TransferenciaForm()
    
    return render(request, 'finanzas/transferencias/nueva.html', {'form': form})

@login_required
def detalle_transferencia(request, uuid):
    """Vista para ver detalles de una transferencia específica"""
    # Buscar la transferencia por UUID y verificar que el usuario sea parte de ella
    transferencia = get_object_or_404(
        Transferencia.objects.filter(
            Q(emisor=request.user) | Q(receptor=request.user)
        ),
        uuid=uuid
    )
    
    context = {
        'transferencia': transferencia,
        'es_emisor': transferencia.emisor == request.user
    }
    
    return render(request, 'finanzas/transferencias/detalle.html', context)

@login_required
def cancelar_transferencia(request, uuid):
    """Vista para cancelar una transferencia pendiente"""
    if request.method == 'POST':
        # Solo el emisor puede cancelar una transferencia
        transferencia = get_object_or_404(Transferencia, uuid=uuid, emisor=request.user)
        
        if transferencia.estado != 'pending':
            messages.error(request, "Solo se pueden cancelar transferencias pendientes.")
            return redirect('finanzas:detalle_transferencia', uuid=uuid)
        
        if transferencia.cancelar():
            messages.success(request, "La transferencia ha sido cancelada correctamente.")
        else:
            messages.error(request, "No se pudo cancelar la transferencia.")
            
    return redirect('finanzas:detalle_transferencia', uuid=uuid)

def calcular_saldo_usuario(user):
    """Función auxiliar para calcular el saldo disponible de un usuario"""
    ingresos = Transaccion.objects.filter(usuario=user, tipo='ingreso').values_list('monto', flat=True)
    gastos = Transaccion.objects.filter(usuario=user, tipo='gasto').values_list('monto', flat=True)
    
    total_ingresos = sum(ingresos) if ingresos else 0
    total_gastos = sum(gastos) if gastos else 0
    
    return total_ingresos - total_gastos
