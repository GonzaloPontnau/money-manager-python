import logging
import time

from django.conf import settings

from chatbot.models import ConversationMessage
from chatbot.prompts import FINANCIAL_ASSISTANT_PROMPT
from chatbot.services.embedding_service import get_embedding
from chatbot.services.financial_context import build_financial_context
from chatbot.services.followup_detector import detect_intent
from chatbot.services.llm_service import call_groq
from chatbot.services.qdrant_service import search_similar

logger = logging.getLogger(__name__)


def _format_rag_results(results):
    if not results:
        return "No se encontraron transacciones relevantes."

    lines = []
    for hit in results:
        payload = hit.payload
        tipo = "Ingreso" if payload.get("tipo") == "ingreso" else "Gasto"
        cat = payload.get("categoria", "Sin categoría") or "Sin categoría"
        desc = payload.get("descripcion", "")
        fecha = payload.get("fecha", "")[:10] if payload.get("fecha") else ""
        monto = payload.get("monto", 0)
        line = f"- {tipo}: ${monto:.2f} | {cat} | {fecha}"
        if desc:
            line += f" | {desc}"
        lines.append(line)

    return "\n".join(lines)


def process_message(user, message, session_id):
    start = time.monotonic()
    logger.info(
        "Pipeline inicio: user=%s session=%s msg_len=%d",
        user.username,
        session_id[:8],
        len(message),
    )

    ConversationMessage.objects.create(
        usuario=user,
        session_id=session_id,
        role="user",
        content=message,
    )

    max_history = settings.CHATBOT_MAX_HISTORY
    history = list(
        ConversationMessage.objects.filter(usuario=user, session_id=session_id)
        .order_by("-created_at")[: max_history + 1]
    )
    history.reverse()

    last_bot_was_followup = False
    for msg in reversed(history[:-1]):
        if msg.role == "assistant":
            last_bot_was_followup = msg.is_followup_question
            break

    intent, needs_followup, followup_msg, followup_options = detect_intent(
        message,
        last_bot_was_followup,
    )

    if needs_followup:
        logger.info("Follow-up detectado: intent=%s session=%s", intent, session_id[:8])
        ConversationMessage.objects.create(
            usuario=user,
            session_id=session_id,
            role="assistant",
            content=followup_msg,
            is_followup_question=True,
        )
        return {
            "response": followup_msg,
            "is_followup": True,
            "followup_options": followup_options,
            "session_id": session_id,
        }

    financial_context = build_financial_context(user)

    rag_text = "No se encontraron transacciones relevantes."
    embedding = get_embedding(message)
    if embedding:
        results = search_similar(embedding, user.id, limit=5)
        rag_text = _format_rag_results(results)

    system_prompt = FINANCIAL_ASSISTANT_PROMPT.format(
        financial_context=financial_context,
        rag_results=rag_text,
    )

    llm_messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        if msg.role in ("user", "assistant"):
            llm_messages.append({"role": msg.role, "content": msg.content})

    response_text = call_groq(llm_messages)
    if response_text is None:
        response_text = (
            "Lo siento, hubo un problema al procesar tu consulta. "
            "Por favor, intenta de nuevo en unos momentos."
        )

    ConversationMessage.objects.create(
        usuario=user,
        session_id=session_id,
        role="assistant",
        content=response_text,
        is_followup_question=False,
    )

    elapsed = time.monotonic() - start
    logger.info(
        "Pipeline fin: user=%s session=%s elapsed=%.2fs chars_resp=%d",
        user.username,
        session_id[:8],
        elapsed,
        len(response_text),
    )

    return {
        "response": response_text,
        "is_followup": False,
        "followup_options": None,
        "session_id": session_id,
    }

