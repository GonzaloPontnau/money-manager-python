from django.core.management.base import BaseCommand

from finanzas.models.transaccion import Transaccion
from chatbot.services.embedding_service import get_embedding
from chatbot.services.qdrant_service import upsert_transaction, ensure_collection
from chatbot.signals import _generate_transaction_text


class Command(BaseCommand):
    help = 'Generate embeddings for all existing transactions and store in Qdrant'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Only embed transactions for a specific user ID',
        )

    def handle(self, *args, **options):
        if not ensure_collection():
            self.stderr.write(self.style.ERROR(
                'Failed to ensure Qdrant collection. Check QDRANT_URL and QDRANT_API_KEY.'
            ))
            return

        queryset = Transaccion.objects.select_related('categoria', 'usuario')

        user_id = options.get('user_id')
        if user_id:
            queryset = queryset.filter(usuario_id=user_id)

        total = queryset.count()
        self.stdout.write(f'Embedding {total} transactions...')

        success = 0
        failed = 0

        for transaction in queryset.iterator():
            text = _generate_transaction_text(transaction)
            embedding = get_embedding(text)

            if embedding and upsert_transaction(transaction, embedding):
                success += 1
            else:
                failed += 1

            if (success + failed) % 10 == 0:
                self.stdout.write(f'  Progress: {success + failed}/{total}')

        self.stdout.write(self.style.SUCCESS(
            f'Done. Success: {success}, Failed: {failed}, Total: {total}'
        ))
