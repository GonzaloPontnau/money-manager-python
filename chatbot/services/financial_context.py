import logging
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from finanzas.models import Categoria, Presupuesto, Transaccion

logger = logging.getLogger(__name__)


def build_financial_context(user):
    parts = []

    totals = (
        Transaccion.objects.filter(usuario=user)
        .values("tipo")
        .annotate(total=Sum("monto"))
    )

    ingresos = Decimal("0")
    gastos = Decimal("0")
    for item in totals:
        if item["tipo"] == "ingreso":
            ingresos = item["total"] or Decimal("0")
        elif item["tipo"] == "gasto":
            gastos = item["total"] or Decimal("0")

    balance = ingresos - gastos
    parts.append(
        f"Balance actual: ${balance:.2f} (Ingresos totales: ${ingresos:.2f}, Gastos totales: ${gastos:.2f})"
    )

    now = timezone.now()
    category_spending = (
        Transaccion.objects.filter(
            usuario=user,
            tipo="gasto",
            fecha__year=now.year,
            fecha__month=now.month,
        )
        .values("categoria__nombre")
        .annotate(total=Sum("monto"))
        .order_by("-total")
    )

    if category_spending:
        lines = [f"Gastos de {now.strftime('%B %Y')} por categoría:"]
        for item in category_spending:
            categoria = item["categoria__nombre"] or "Sin categoría"
            lines.append(f"  - {categoria}: ${item['total']:.2f}")
        parts.append("\n".join(lines))

    budgets = Presupuesto.objects.filter(usuario=user, mes=now.month, año=now.year).select_related("categoria")
    if budgets.exists():
        lines = ["Estado de presupuestos (mes actual):"]
        for budget in budgets:
            spent = budget.get_gasto_actual()
            pct = budget.get_porcentaje_usado()
            status = "EXCEDIDO" if budget.esta_excedido else f"{pct:.0f}%"
            lines.append(
                f"  - {budget.categoria.nombre}: ${spent:.2f} / ${budget.monto_maximo:.2f} ({status})"
            )
        parts.append("\n".join(lines))

    recent = (
        Transaccion.objects.filter(usuario=user)
        .select_related("categoria")
        .order_by("-fecha")[:10]
    )

    if recent:
        lines = ["Últimas 10 transacciones:"]
        for tx in recent:
            sign = "+" if tx.tipo == "ingreso" else "-"
            categoria = tx.categoria.nombre if tx.categoria else "Sin categoría"
            desc = f" - {tx.descripcion}" if tx.descripcion else ""
            lines.append(
                f"  {sign}${tx.monto:.2f} | {categoria} | {tx.fecha.strftime('%d/%m/%Y')}{desc}"
            )
        parts.append("\n".join(lines))

    categories = Categoria.objects.filter(usuario=user).values_list("nombre", "tipo")
    if categories:
        income_cats = [name for name, ctype in categories if ctype == "ingreso"]
        expense_cats = [name for name, ctype in categories if ctype == "gasto"]
        parts.append(f"Categorías de ingreso: {', '.join(income_cats) if income_cats else 'Sin categorías'}")
        parts.append(f"Categorías de gasto: {', '.join(expense_cats) if expense_cats else 'Sin categorías'}")

    return "\n\n".join(parts)

