import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def call_groq(messages, temperature=0.3, max_tokens=None):
    """
    Call the Groq API with assembled messages.
    Uses the OpenAI-compatible chat completions format.

    Returns the assistant's response text, or None on failure.
    """
    if not settings.GROQ_API_KEY:
        logger.error("GROQ_API_KEY is not configured")
        return None

    max_tokens = max_tokens or settings.CHATBOT_MAX_TOKENS

    try:
        response = requests.post(
            GROQ_API_URL,
            json={
                "model": settings.GROQ_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=25,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        logger.error("Groq API request timed out")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Groq API error: {e}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected Groq API response format: {e}")
        return None
