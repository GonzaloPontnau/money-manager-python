import logging
import time

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MAX_RETRIES = 2
RETRY_DELAY = 1.5  # seconds


def call_groq(messages, temperature=0.3, max_tokens=None):
    """
    Call the Groq API with assembled messages.
    Uses the OpenAI-compatible chat completions format.
    Retries once on transient failures.

    Returns the assistant's response text, or None on failure.
    """
    if not settings.GROQ_API_KEY:
        logger.error("GROQ_API_KEY is not configured")
        return None

    max_tokens = max_tokens or settings.CHATBOT_MAX_TOKENS
    model = settings.GROQ_MODEL
    logger.info("Calling Groq API with model=%s, max_tokens=%d", model, max_tokens)

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                GROQ_API_URL,
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            logger.info("Groq API success on attempt %d, response_len=%d", attempt, len(content))
            return content
        except requests.exceptions.Timeout:
            last_error = "timeout"
            logger.warning("Groq API timeout on attempt %d/%d", attempt, MAX_RETRIES)
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            # Log response body for HTTP errors to help debugging
            resp_body = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    resp_body = e.response.text[:500]
                except Exception:
                    resp_body = "(could not read response body)"
            logger.error("Groq API error on attempt %d/%d: %s | response: %s", attempt, MAX_RETRIES, e, resp_body)
        except (KeyError, IndexError) as e:
            logger.error("Unexpected Groq API response format: %s", e)
            return None  # Don't retry on format errors

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    logger.error("Groq API failed after %d attempts. Last error: %s", MAX_RETRIES, last_error)
    return None
