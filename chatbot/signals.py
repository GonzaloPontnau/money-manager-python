import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from finanzas.models.transaccion import Transaccion

logger = logging.getLogger(__name__)


def _generate_transaction_text(transaction):
    """Generate natural language text for embedding a transaction."""
    tipo = "Ingreso" if transaction.tipo == 'ingreso' else "Gasto"
    categoria = transaction.categoria.nombre if transaction.categoria else "Sin categoría"
    fecha = transaction.fecha.strftime('%d/%m/%Y')
    descripcion = transaction.descripcion or ""
    return f"{tipo} de ${transaction.monto} en categoría {categoria} el {fecha}: {descripcion}".strip()


@receiver(post_save, sender=Transaccion)
def embed_transaction_on_save(sender, instance, **kwargs):
    """Generate and store embedding when a transaction is created/updated."""
    try:
        from chatbot.services.embedding_service import get_embedding
        from chatbot.services.qdrant_service import upsert_transaction

        text = _generate_transaction_text(instance)
        embedding = get_embedding(text)
        if embedding:
            upsert_transaction(instance, embedding)
    except Exception as e:
        logger.warning(f"Failed to embed transaction {instance.id}: {e}")


@receiver(post_delete, sender=Transaccion)
def remove_transaction_embedding(sender, instance, **kwargs):
    """Remove embedding when transaction is deleted."""
    try:
        from chatbot.services.qdrant_service import delete_point
        delete_point(instance.id)
    except Exception as e:
        logger.warning(f"Failed to remove embedding for transaction {instance.id}: {e}")
