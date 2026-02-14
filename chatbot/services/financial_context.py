from decimal import Decimal

from django.db.models import Sum, Q
from django.utils import timezone

from finanzas.models.transaccion import Transaccion
from finanzas.models.categoria import Categoria


def build_financial_context(user):
    """
    Build a structured text summary of the user's financial data.
    This is injected into the LLM prompt as context.
    """
    parts = []

    # Current balance
    totals = (
        Transaccion.objects.filter(usuario=user)
        .values('tipo')
        .annotate(total=Sum('monto'))
    )
    ingresos = Decimal('0')
    gastos = Decimal('0')
    for item in totals:
        if item['tipo'] == 'ingreso':
            ingresos = item['total'] or Decimal('0')
        elif item['tipo'] == 'gasto':
            gastos = item['total'] or Decimal('0')

    balance = ingresos - gastos
    parts.append(
        f"Balance actual: ${balance:.2f} "
        f"(Ingresos totales: ${ingresos:.2f}, Gastos totales: ${gastos:.2f})"
    )

    # Current month spending by category
    now = timezone.now()
    month_transactions = Transaccion.objects.filter(
        usuario=user,
        tipo='gasto',
        fecha__year=now.year,
        fecha__month=now.month,
    ).select_related('categoria')

    category_spending = (
        month_transactions
        .values('categoria__nombre')
        .annotate(total=Sum('monto'))
        .order_by('-total')
    )

    if category_spending:
        lines = [f"Gastos de {now.strftime('%B %Y')} por categoría:"]
        for item in category_spending:
            cat = item['categoria__nombre'] or 'Sin categoría'
            lines.append(f"  - {cat}: ${item['total']:.2f}")
        parts.append("\n".join(lines))

    # Budget status
    try:
        from finanzas.models.presupuesto import Presupuesto

        budgets = Presupuesto.objects.filter(
            usuario=user,
            mes=now.month,
            año=now.year,
        ).select_related('categoria')

        if budgets.exists():
            lines = ["Estado de presupuestos (mes actual):"]
            for b in budgets:
                spent = b.get_gasto_actual()
                pct = b.get_porcentaje_usado()
                status = "EXCEDIDO" if b.esta_excedido else f"{pct:.0f}%"
                lines.append(
                    f"  - {b.categoria.nombre}: ${spent:.2f} / ${b.monto_maximo:.2f} ({status})"
                )
            parts.append("\n".join(lines))
    except Exception:
        pass

    # Recent transactions (last 10)
    recent = (
        Transaccion.objects.filter(usuario=user)
        .select_related('categoria')
        .order_by('-fecha')[:10]
    )

    if recent:
        lines = ["Últimas 10 transacciones:"]
        for t in recent:
            tipo = "+" if t.tipo == 'ingreso' else "-"
            cat = t.categoria.nombre if t.categoria else 'Sin categoría'
            desc = f" - {t.descripcion}" if t.descripcion else ""
            lines.append(
                f"  {tipo}${t.monto:.2f} | {cat} | {t.fecha.strftime('%d/%m/%Y')}{desc}"
            )
        parts.append("\n".join(lines))

    # User categories
    categories = Categoria.objects.filter(usuario=user).values_list('nombre', 'tipo')
    if categories:
        income_cats = [c[0] for c in categories if c[1] == 'ingreso']
        expense_cats = [c[0] for c in categories if c[1] == 'gasto']
        parts.append(f"Categorías de ingreso: {', '.join(income_cats)}")
        parts.append(f"Categorías de gasto: {', '.join(expense_cats)}")

    return "\n\n".join(parts)
