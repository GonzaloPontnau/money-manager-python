import logging

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from finanzas.models import Transaccion

logger = logging.getLogger(__name__)


def _generate_transaction_text(transaction):
    tipo = "Ingreso" if transaction.tipo == "ingreso" else "Gasto"
    categoria = transaction.categoria.nombre if transaction.categoria else "Sin categoria"
    fecha = transaction.fecha.strftime("%d/%m/%Y")
    descripcion = transaction.descripcion or ""
    return (
        f"{tipo} de ${transaction.monto} en categoria {categoria} el {fecha}: {descripcion}".strip()
    )


@receiver(post_save, sender=Transaccion)
def embed_transaction_on_save(sender, instance, **kwargs):
    if not settings.CHATBOT_EMBEDDINGS_ENABLED:
        return

    try:
        from chatbot.services.embedding_service import get_embedding
        from chatbot.services.qdrant_service import upsert_transaction

        text = _generate_transaction_text(instance)
        embedding = get_embedding(text)
        if embedding:
            upsert_transaction(instance, embedding)
    except Exception as exc:
        logger.warning("Failed to embed transaction %s: %s", instance.id, exc)


@receiver(post_delete, sender=Transaccion)
def remove_transaction_embedding(sender, instance, **kwargs):
    if not settings.CHATBOT_EMBEDDINGS_ENABLED:
        return

    try:
        from chatbot.services.qdrant_service import delete_point

        delete_point(instance.id)
    except Exception as exc:
        logger.warning("Failed to remove embedding for transaction %s: %s", instance.id, exc)
