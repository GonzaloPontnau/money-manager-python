import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

HF_EMBEDDING_URL = (
    "https://api-inference.huggingface.co/pipeline/feature-extraction/"
    "sentence-transformers/all-MiniLM-L6-v2"
)
EMBEDDING_DIM = 384


def get_embedding(text):
    """
    Get a 384-dimensional embedding vector via HuggingFace Inference API.
    Returns a list of floats, or None on failure.
    """
    if not settings.HF_API_TOKEN:
        logger.warning("HF_API_TOKEN is not configured, skipping embedding")
        return None

    try:
        response = requests.post(
            HF_EMBEDDING_URL,
            headers={"Authorization": f"Bearer {settings.HF_API_TOKEN}"},
            json={"inputs": text, "options": {"wait_for_model": True}},
            timeout=15,
        )
        response.raise_for_status()
        embedding = response.json()

        # The API returns a list of floats for single input
        if isinstance(embedding, list) and len(embedding) == EMBEDDING_DIM:
            return embedding
        # Sometimes wrapped in an extra list
        if isinstance(embedding, list) and len(embedding) == 1:
            return embedding[0]

        logger.warning(f"Unexpected embedding shape: {type(embedding)}")
        return None
    except requests.exceptions.Timeout:
        logger.error("HuggingFace embedding API timed out")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"HuggingFace embedding API error: {e}")
        return None
