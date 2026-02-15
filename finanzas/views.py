import json
import logging
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from finanzas.forms import RegisterForm, TransaccionForm, TransferenciaForm
from finanzas.models import Categoria, Transaccion, Transferencia

logger = logging.getLogger(__name__)

CATEGORY_COLORS = [
    "#2E7D32",
    "#1565C0",
    "#00838F",
    "#F9A825",
    "#EF6C00",
    "#6A1B9A",
    "#C62828",
    "#4E342E",
]

# Payload estático para la demo sin login
DEMO_PAYLOAD = {
    "ingresos_totales": 4850.0,
    "gastos_totales": 2120.5,
    "balance": 2729.5,
    "gastos_por_categoria": [
        {"id": None, "nombre": "Alimentación", "monto": 420.0, "color": "#2E7D32"},
        {"id": None, "nombre": "Transporte", "monto": 180.5, "color": "#1565C0"},
        {"id": None, "nombre": "Vivienda", "monto": 650.0, "color": "#00838F"},
        {"id": None, "nombre": "Entretenimiento", "monto": 95.0, "color": "#F9A825"},
        {"id": None, "nombre": "Servicios", "monto": 275.0, "color": "#EF6C00"},
        {"id": None, "nombre": "Otros", "monto": 500.0, "color": "#6A1B9A"},
    ],
    "tiene_datos_demo": True,
}


def _build_dashboard_payload(user):
    totales = (
        Transaccion.objects.filter(usuario=user)
        .values("tipo")
        .annotate(total=Sum("monto"))
        .order_by("tipo")
    )

    ingresos_totales = 0
    gastos_totales = 0
    for item in totales:
        if item["tipo"] == "ingreso":
            ingresos_totales = item["total"] or 0
        elif item["tipo"] == "gasto":
            gastos_totales = item["total"] or 0

    gastos_por_categoria_raw = (
        Transaccion.objects.filter(usuario=user, tipo="gasto")
        .values("categoria__id", "categoria__nombre")
        .annotate(monto=Sum("monto"))
        .order_by("-monto")
    )

    gastos_por_categoria = []
    for index, item in enumerate(gastos_por_categoria_raw):
        nombre = item["categoria__nombre"] or "Sin categoría"
        color = CATEGORY_COLORS[index % len(CATEGORY_COLORS)]
        gastos_por_categoria.append(
            {
                "id": item["categoria__id"],
                "nombre": nombre,
                "monto": float(item["monto"] or 0),
                "color": color,
            }
        )

    tiene_datos_demo = Transaccion.objects.filter(
        usuario=user, descripcion__startswith="[DEMO]"
    ).exists()

    return {
        "ingresos_totales": float(ingresos_totales),
        "gastos_totales": float(gastos_totales),
        "balance": float(ingresos_totales - gastos_totales),
        "gastos_por_categoria": gastos_por_categoria,
        "tiene_datos_demo": tiene_datos_demo,
    }


def _crear_datos_demo(usuario):
    # 1. Create Categories if they don't exist
    categorias_data = [
        ('Salario', 'ingreso'),
        ('Freelance', 'ingreso'),
        ('Inversiones', 'ingreso'),
        ('Alimentación', 'gasto'),
        ('Transporte', 'gasto'),
        ('Vivienda', 'gasto'),
        ('Entretenimiento', 'gasto'),
        ('Salud', 'gasto'),
        ('Educación', 'gasto'),
        ('Servicios', 'gasto'),
    ]

    categorias = {}
    for nombre, tipo in categorias_data:
        cat, _ = Categoria.objects.get_or_create(
            usuario=usuario,
            nombre=nombre,
            defaults={'tipo': tipo}
        )
        categorias[nombre] = cat

    # 2. Check if demo data already exists (by description tag)
    if Transaccion.objects.filter(usuario=usuario, descripcion__startswith="[DEMO]").exists():
        return 0

    # 3. Create Transactions (Last 3 months)
    today = timezone.now()
    
    descriptions = {
        'Salario': ['Sueldo mensual', 'Bono'],
        'Freelance': ['Proyecto web', 'Consultoría'],
        'Inversiones': ['Dividendos', 'Intereses'],
        'Alimentación': ['Supermercado', 'Restaurante', 'Café'],
        'Transporte': ['Gasolina', 'Uber', 'Bus'],
        'Vivienda': ['Alquiler', 'Reparaciones'],
        'Entretenimiento': ['Cine', 'Netflix', 'Juegos'],
        'Salud': ['Farmacia', 'Consulta médica'],
        'Educación': ['Libros', 'Curso online'],
        'Servicios': ['Luz', 'Agua', 'Internet'],
    }

    transactions_to_create = []
    # Generate ~50 transactions
    for _ in range(50):
        cat_name = random.choice(list(categorias.keys()))
        cat = categorias[cat_name]
        
        if cat.tipo == 'ingreso':
            monto = Decimal(random.uniform(1000, 5000)).quantize(Decimal('0.01'))
        else:
            monto = Decimal(random.uniform(10, 200)).quantize(Decimal('0.01'))

        days_offset = random.randint(0, 90)
        trans_date = today - timedelta(days=days_offset)
        
        desc_list = descriptions.get(cat_name, ['Transacción'])
        desc = random.choice(desc_list)

        transactions_to_create.append(Transaccion(
            usuario=usuario,
            fecha=trans_date,
            monto=monto,
            tipo=cat.tipo,
            categoria=cat,
            descripcion=f"[DEMO] {desc}"
        ))
    
    Transaccion.objects.bulk_create(transactions_to_create)
    creadas = len(transactions_to_create)

    # 4. Create Budgets (optional, but requested in plan)
    # Check if budget exists, if not create
    from finanzas.models import Presupuesto # Local import to avoid circular dependency if any
    
    current_month = today.month
    current_year = today.year
    budget_cats = ['Alimentación', 'Transporte', 'Entretenimiento']
    
    for cat_name in budget_cats:
        if cat_name in categorias:
            cat = categorias[cat_name]
            amount = Decimal(random.uniform(500, 1500)).quantize(Decimal('0.01'))
            
            Presupuesto.objects.get_or_create(
                usuario=usuario,
                categoria=cat,
                mes=current_month,
                año=current_year,
                defaults={'monto_maximo': amount}
            )

    return creadas


# Authentication

def login_view(request):
    if request.user.is_authenticated:
        return redirect("finanzas:dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                logger.info("Login exitoso: user=%s", username)
                messages.success(request, f"Bienvenido, {username}!")
                return redirect("finanzas:dashboard")

            logger.warning("Login fallido (authenticate): user=%s", username)
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
        else:
            logger.warning(
                "Login fallido (form inválido): ip=%s",
                request.META.get("REMOTE_ADDR"),
            )
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()

    return render(request, "finanzas/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("finanzas:dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                logger.info("Nuevo usuario registrado: user=%s (id=%d)", user.username, user.id)
                messages.success(request, "Cuenta creada exitosamente")
                return redirect("finanzas:dashboard")
            except Exception as e:
                # Catch IntegrityError or other db errors (e.g. double submission)
                logger.error(f"Error al registrar usuario: {e}")
                if "UNIQUE constraint failed" in str(e):
                     messages.warning(request, "El usuario ya existe o hubo un doble envío. Intenta iniciar sesión.")
                     return redirect("finanzas:login")
                else:
                    messages.error(request, "Error interno al crear la cuenta. Inténtalo de nuevo.")

        logger.warning("Registro fallido: errores=%s", form.errors)
        messages.error(request, "Error al crear la cuenta. Revisa los datos.")
    else:
        form = RegisterForm()

    return render(request, "finanzas/register.html", {"form": form})


@login_required
def logout_view(request):
    username = request.user.username
    logout(request)
    logger.info("Logout: user=%s", username)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("finanzas:login")


# Dashboard

@login_required
def dashboard_view(request):
    payload = _build_dashboard_payload(request.user)
    transacciones = (
        Transaccion.objects.filter(usuario=request.user)
        .select_related("categoria")
        .order_by("-fecha")[:5]
    )

    context = {
        "ingresos_totales": payload["ingresos_totales"],
        "gastos_totales": payload["gastos_totales"],
        "balance": payload["balance"],
        "transacciones": transacciones,
        "gastos_por_categoria": payload["gastos_por_categoria"],
        "gastos_por_categoria_json": json.dumps(payload["gastos_por_categoria"]),
        "tiene_datos_demo": payload["tiene_datos_demo"],
        "is_demo": False,
    }
    return render(request, "finanzas/dashboard.html", context)


def demo_view(request):
    """Dashboard de solo lectura con datos estáticos, sin requerir login."""
    context = {
        "ingresos_totales": DEMO_PAYLOAD["ingresos_totales"],
        "gastos_totales": DEMO_PAYLOAD["gastos_totales"],
        "balance": DEMO_PAYLOAD["balance"],
        "transacciones": [],
        "gastos_por_categoria": DEMO_PAYLOAD["gastos_por_categoria"],
        "gastos_por_categoria_json": json.dumps(DEMO_PAYLOAD["gastos_por_categoria"]),
        "tiene_datos_demo": True,
        "is_demo": True,
    }
    return render(request, "finanzas/dashboard.html", context)


def demo_data_api(request):
    """API con payload estático para el polling del dashboard demo."""
    return JsonResponse(DEMO_PAYLOAD)


@login_required
def dashboard_data_api(request):
    payload = _build_dashboard_payload(request.user)
    return JsonResponse(payload)


@login_required
def cargar_datos_demo(request):
    if request.method != "POST":
        return redirect("finanzas:dashboard")

    creadas = _crear_datos_demo(request.user)
    if creadas:
        messages.success(request, "Datos demo cargados. Ya puedes ver los charts con movimiento.")
    else:
        messages.info(request, "Ya tenias datos demo cargados en tu cuenta.")

    return redirect("finanzas:dashboard")


# Transacciones

@login_required
def lista_transacciones(request):
    tipo = request.GET.get("tipo")
    categoria_id = request.GET.get("categoria")

    transacciones = Transaccion.objects.filter(usuario=request.user).select_related("categoria")

    if tipo and tipo in dict(Transaccion.TIPO_CHOICES):
        transacciones = transacciones.filter(tipo=tipo)

    if categoria_id:
        transacciones = transacciones.filter(categoria_id=categoria_id)

    transacciones = transacciones.order_by("-fecha")

    categorias = list(Categoria.objects.filter(usuario=request.user))
    payload = _build_dashboard_payload(request.user)

    context = {
        "transacciones": transacciones,
        "categorias": categorias,
        "tipo_seleccionado": tipo,
        "categoria_seleccionada": categoria_id,
        "ingresos_totales": payload["ingresos_totales"],
        "gastos_totales": payload["gastos_totales"],
        "balance": payload["balance"],
    }
    return render(request, "finanzas/transacciones/lista.html", context)


@login_required
def nueva_transaccion(request):
    if request.method == "POST":
        form = TransaccionForm(request.POST, request.FILES, usuario=request.user)
        if form.is_valid():
            transaccion = form.save()
            logger.info(
                "Nueva transacción: id=%d tipo=%s monto=%s user=%s",
                transaccion.id,
                transaccion.tipo,
                transaccion.monto,
                request.user.username,
            )
            messages.success(request, "Transacción registrada correctamente")

            if "guardar_continuar" in request.POST:
                return redirect("finanzas:nueva_transaccion")
            return redirect("finanzas:lista_transacciones")
    else:
        tipo_inicial = request.GET.get("tipo", "")
        if tipo_inicial:
            form = TransaccionForm(usuario=request.user, initial={"tipo": tipo_inicial})
        else:
            form = TransaccionForm(usuario=request.user)

    return render(
        request,
        "finanzas/transacciones/formulario.html",
        {
            "form": form,
            "title": "Nueva Transacción",
        },
    )


@login_required
def editar_transaccion(request, id):
    transaccion = get_object_or_404(Transaccion, id=id, usuario=request.user)

    if request.method == "POST":
        form = TransaccionForm(
            request.POST,
            request.FILES,
            usuario=request.user,
            instance=transaccion,
        )
        if form.is_valid():
            form.save()
            logger.info("Transacción editada: id=%d user=%s", transaccion.id, request.user.username)
            messages.success(request, "Transacción actualizada correctamente")
            return redirect("finanzas:lista_transacciones")
    else:
        form = TransaccionForm(usuario=request.user, instance=transaccion)

    return render(
        request,
        "finanzas/transacciones/formulario.html",
        {
            "form": form,
            "title": "Editar Transacción",
            "transaccion": transaccion,
        },
    )


@login_required
def eliminar_transaccion(request, id):
    transaccion = get_object_or_404(Transaccion, id=id, usuario=request.user)

    if request.method == "POST":
        logger.info("Transacción eliminada: id=%d user=%s", transaccion.id, request.user.username)
        transaccion.delete()
        messages.success(request, "Transacción eliminada correctamente")
        return redirect("finanzas:lista_transacciones")

    return render(
        request,
        "finanzas/transacciones/confirmar_eliminar.html",
        {
            "transaccion": transaccion,
        },
    )


@login_required
def detalle_transaccion(request, id):
    transaccion = get_object_or_404(Transaccion, id=id, usuario=request.user)
    return render(request, "finanzas/transacciones/detalle.html", {"transaccion": transaccion})


@login_required
def filtrar_categorias(request):
    tipo = request.GET.get("tipo", "")
    categorias = []

    if tipo in dict(Transaccion.TIPO_CHOICES):
        categorias = list(
            Categoria.objects.filter(usuario=request.user, tipo=tipo).values("id", "nombre")
        )

    return JsonResponse({"categorias": categorias})


# Transferencias

@login_required
def lista_transferencias(request):
    transferencias = (
        Transferencia.objects.filter(Q(emisor=request.user) | Q(receptor=request.user))
        .select_related("emisor", "receptor")
        .order_by("-fecha_creacion")
    )

    enviadas = [t for t in transferencias if t.emisor_id == request.user.id]
    recibidas = [t for t in transferencias if t.receptor_id == request.user.id]

    return render(
        request,
        "finanzas/transferencias/lista.html",
        {
            "transferencias": transferencias,
            "enviadas": enviadas,
            "recibidas": recibidas,
        },
    )


@login_required
def nueva_transferencia(request):
    if request.method == "POST":
        form = TransferenciaForm(request.POST, emisor=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    transferencia = form.save(commit=False)
                    transferencia.emisor = request.user

                    if transferencia.receptor_id == request.user.id:
                        messages.error(request, "No puedes transferirte dinero a ti mismo.")
                        return render(request, "finanzas/transferencias/nueva.html", {"form": form})

                    user_ids = sorted({request.user.id, transferencia.receptor_id})
                    locked_users = {
                        u.id: u
                        for u in User.objects.select_for_update().filter(id__in=user_ids).order_by("id")
                    }

                    emisor = locked_users.get(request.user.id)
                    receptor = locked_users.get(transferencia.receptor_id)
                    if emisor is None or receptor is None:
                        messages.error(request, "No se pudo bloquear a los usuarios de la transferencia.")
                        return render(request, "finanzas/transferencias/nueva.html", {"form": form})

                    saldo_actual = _calcular_saldo(emisor)
                    if saldo_actual < transferencia.monto:
                        messages.error(
                            request,
                            f"No tienes saldo suficiente. Tu saldo actual es: {saldo_actual}",
                        )
                        return render(request, "finanzas/transferencias/nueva.html", {"form": form})

                    transferencia.save()

                    categoria_gasto = (
                        Categoria.objects.filter(
                            usuario=emisor,
                            tipo="gasto",
                            nombre="Transferencia enviada",
                        ).first()
                        or Categoria.objects.filter(usuario=emisor, tipo="gasto").first()
                    )

                    categoria_ingreso = (
                        Categoria.objects.filter(
                            usuario=receptor,
                            tipo="ingreso",
                            nombre="Transferencia recibida",
                        ).first()
                        or Categoria.objects.filter(usuario=receptor, tipo="ingreso").first()
                    )

                    Transaccion.objects.create(
                        usuario=emisor,
                        fecha=timezone.now(),
                        monto=transferencia.monto,
                        tipo="gasto",
                        categoria=categoria_gasto,
                        descripcion=f"Transferencia a {receptor.username}: {transferencia.concepto}",
                    )

                    Transaccion.objects.create(
                        usuario=receptor,
                        fecha=timezone.now(),
                        monto=transferencia.monto,
                        tipo="ingreso",
                        categoria=categoria_ingreso,
                        descripcion=f"Transferencia de {emisor.username}: {transferencia.concepto}",
                    )

                    transferencia.completar()

                messages.success(
                    request,
                    f"Transferencia de {transferencia.monto} realizada con éxito a {transferencia.receptor.username}",
                )
                messages.info(
                    request,
                    "El procesamiento completo de la transferencia puede demorar unos minutos.",
                )
                return redirect("finanzas:lista_transferencias")
            except Exception as exc:
                logger.exception("Error al realizar transferencia")
                messages.error(request, f"Error al realizar la transferencia: {exc}")
    else:
        form = TransferenciaForm(emisor=request.user)

    return render(request, "finanzas/transferencias/nueva.html", {"form": form})


@login_required
def detalle_transferencia(request, uuid):
    transferencia = get_object_or_404(
        Transferencia.objects.select_related("emisor", "receptor").filter(
            Q(emisor=request.user) | Q(receptor=request.user)
        ),
        uuid=uuid,
    )

    return render(
        request,
        "finanzas/transferencias/detalle.html",
        {
            "transferencia": transferencia,
            "es_emisor": transferencia.emisor_id == request.user.id,
        },
    )


@login_required
def cancelar_transferencia(request, uuid):
    if request.method == "POST":
        transferencia = get_object_or_404(Transferencia, uuid=uuid, emisor=request.user)

        if transferencia.estado != "pending":
            messages.error(request, "Solo se pueden cancelar transferencias pendientes.")
            return redirect("finanzas:detalle_transferencia", uuid=uuid)

        if transferencia.cancelar():
            messages.success(request, "La transferencia ha sido cancelada correctamente.")
        else:
            messages.error(request, "No se pudo cancelar la transferencia.")

    return redirect("finanzas:detalle_transferencia", uuid=uuid)


# Helpers

def _calcular_saldo(user):
    ingresos = (
        Transaccion.objects.filter(usuario=user, tipo="ingreso").aggregate(total=Sum("monto"))["total"]
        or 0
    )
    gastos = (
        Transaccion.objects.filter(usuario=user, tipo="gasto").aggregate(total=Sum("monto"))["total"]
        or 0
    )
    return ingresos - gastos

