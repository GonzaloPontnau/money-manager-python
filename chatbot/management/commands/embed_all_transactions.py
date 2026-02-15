from django.core.management.base import BaseCommand

from chatbot.services.embedding_service import get_embedding
from chatbot.services.qdrant_service import ensure_collection, upsert_transaction
from chatbot.signals import _generate_transaction_text
from finanzas.models import Transaccion


class Command(BaseCommand):
    help = "Generate embeddings for existing transactions and store them in Qdrant"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            help="Only process transactions for this user ID",
        )

    def handle(self, *args, **options):
        if not ensure_collection():
            self.stderr.write(
                self.style.ERROR(
                    "Could not ensure Qdrant collection. Check QDRANT_URL/QDRANT_API_KEY."
                )
            )
            return

        queryset = Transaccion.objects.select_related("categoria", "usuario")
        user_id = options.get("user_id")
        if user_id:
            queryset = queryset.filter(usuario_id=user_id)

        total = queryset.count()
        self.stdout.write(f"Embedding {total} transactions...")

        success = 0
        failed = 0
        for tx in queryset.iterator():
            embedding = get_embedding(_generate_transaction_text(tx))
            if embedding and upsert_transaction(tx, embedding):
                success += 1
            else:
                failed += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Success: {success}, Failed: {failed}, Total: {total}"
            )
        )
