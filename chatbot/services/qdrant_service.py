import logging

from django.conf import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "financial_data"
EMBEDDING_DIM = 384

_client = None


def get_client():
    """Get or create a Qdrant client singleton."""
    global _client
    if _client is not None:
        return _client

    if not settings.QDRANT_URL or not settings.QDRANT_API_KEY:
        logger.warning("Qdrant is not configured (QDRANT_URL or QDRANT_API_KEY missing)")
        return None

    try:
        from qdrant_client import QdrantClient
        _client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=10,
        )
        return _client
    except Exception as e:
        logger.error(f"Failed to create Qdrant client: {e}")
        return None


def ensure_collection():
    """Create the collection if it doesn't exist."""
    client = get_client()
    if client is None:
        return False

    try:
        from qdrant_client.models import Distance, VectorParams

        collections = client.get_collections().collections
        existing = [c.name for c in collections]

        if COLLECTION_NAME not in existing:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIM,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
        return True
    except Exception as e:
        logger.error(f"Failed to ensure Qdrant collection: {e}")
        return False


def upsert_transaction(transaction, embedding):
    """Insert or update a transaction vector in Qdrant."""
    client = get_client()
    if client is None:
        return False

    try:
        from qdrant_client.models import PointStruct

        ensure_collection()

        point = PointStruct(
            id=transaction.id,
            vector=embedding,
            payload={
                "user_id": transaction.usuario_id,
                "tipo": transaction.tipo,
                "monto": float(transaction.monto),
                "categoria": (
                    transaction.categoria.nombre if transaction.categoria else None
                ),
                "descripcion": transaction.descripcion or "",
                "fecha": transaction.fecha.isoformat(),
            },
        )
        client.upsert(collection_name=COLLECTION_NAME, points=[point])
        return True
    except Exception as e:
        logger.error(f"Failed to upsert transaction {transaction.id}: {e}")
        return False


def delete_point(transaction_id):
    """Remove a transaction vector from Qdrant."""
    client = get_client()
    if client is None:
        return False

    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=[transaction_id],
        )
        return True
    except Exception as e:
        logger.error(f"Failed to delete point {transaction_id}: {e}")
        return False


def search_similar(query_embedding, user_id, limit=5):
    """Semantic search for similar transactions, filtered by user."""
    client = get_client()
    if client is None:
        return []

    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        ensure_collection()

        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id),
                    )
                ]
            ),
            limit=limit,
        )
        return results
    except Exception as e:
        logger.error(f"Qdrant search failed: {e}")
        return []
