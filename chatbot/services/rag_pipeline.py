import logging
import time

from django.conf import settings

from chatbot.models.conversation import ConversationMessage
from chatbot.services.llm_service import call_groq
from chatbot.services.embedding_service import get_embedding
from chatbot.services.qdrant_service import search_similar
from chatbot.services.financial_context import build_financial_context
from chatbot.services.followup_detector import detect_intent
from chatbot.prompts.system_prompts import FINANCIAL_ASSISTANT_PROMPT

logger = logging.getLogger(__name__)


def _format_rag_results(results):
    """Format Qdrant search results into readable text for the LLM."""
    if not results:
        return "No se encontraron transacciones relevantes."

    lines = []
    for hit in results:
        p = hit.payload
        tipo = "Ingreso" if p.get('tipo') == 'ingreso' else 'Gasto'
        cat = p.get('categoria', 'Sin categoría') or 'Sin categoría'
        desc = p.get('descripcion', '')
        fecha = p.get('fecha', '')[:10] if p.get('fecha') else ''
        monto = p.get('monto', 0)
        line = f"- {tipo}: ${monto:.2f} | {cat} | {fecha}"
        if desc:
            line += f" | {desc}"
        lines.append(line)

    return "\n".join(lines)


def process_message(user, message, session_id):
    """
    Main RAG pipeline. Process a user message and return a response.

    Returns:
        dict with keys: response, is_followup, followup_options, session_id
    """
    t0 = time.monotonic()
    logger.info("Pipeline inicio: user=%s session=%s msg_len=%d", user.username, session_id[:8], len(message))

    # Save user message
    ConversationMessage.objects.create(
        usuario=user,
        session_id=session_id,
        role='user',
        content=message,
    )

    # Load conversation history
    max_history = settings.CHATBOT_MAX_HISTORY
    history = list(
        ConversationMessage.objects.filter(
            usuario=user,
            session_id=session_id,
        ).order_by('-created_at')[:max_history + 1]  # +1 for the message we just saved
    )
    history.reverse()

    # Check if the last bot message was a follow-up question
    last_bot_was_followup = False
    for msg in reversed(history[:-1]):  # exclude the current user message
        if msg.role == 'assistant':
            last_bot_was_followup = msg.is_followup_question
            break

    # Run follow-up detection
    intent, needs_followup, followup_msg, followup_options = detect_intent(
        message, last_bot_was_followup
    )

    if needs_followup:
        logger.info("Follow-up detectado: intent=%s session=%s", intent, session_id[:8])
        # Save follow-up question as assistant message
        ConversationMessage.objects.create(
            usuario=user,
            session_id=session_id,
            role='assistant',
            content=followup_msg,
            is_followup_question=True,
        )
        return {
            'response': followup_msg,
            'is_followup': True,
            'followup_options': followup_options,
            'session_id': session_id,
        }

    # Build financial context from Django models
    financial_context = build_financial_context(user)

    # Semantic search via Qdrant
    rag_text = "No se encontraron transacciones relevantes."
    embedding = get_embedding(message)
    if embedding:
        results = search_similar(embedding, user.id, limit=5)
        rag_text = _format_rag_results(results)

    # Assemble the prompt
    system_prompt = FINANCIAL_ASSISTANT_PROMPT.format(
        financial_context=financial_context,
        rag_results=rag_text,
    )

    # Build messages for the LLM
    llm_messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history (skip system messages)
    for msg in history:
        if msg.role in ('user', 'assistant'):
            llm_messages.append({"role": msg.role, "content": msg.content})

    # Call LLM
    response_text = call_groq(llm_messages)

    if response_text is None:
        response_text = (
            "Lo siento, hubo un problema al procesar tu consulta. "
            "Por favor, intenta de nuevo en unos momentos."
        )

    # Save assistant response
    ConversationMessage.objects.create(
        usuario=user,
        session_id=session_id,
        role='assistant',
        content=response_text,
        is_followup_question=False,
    )

    elapsed = time.monotonic() - t0
    logger.info("Pipeline fin: user=%s session=%s elapsed=%.2fs tokens_resp=%d",
                user.username, session_id[:8], elapsed, len(response_text))

    return {
        'response': response_text,
        'is_followup': False,
        'followup_options': None,
        'session_id': session_id,
    }
