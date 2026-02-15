import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from chatbot.models import ConversationMessage
from chatbot.services.rag_pipeline import process_message

logger = logging.getLogger(__name__)


@login_required
@require_POST
def send_message(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invÃ¡lido"}, status=400)

    user_message = body.get("message", "").strip()
    session_id = body.get("session_id", "").strip()

    if not user_message:
        return JsonResponse({"error": "Mensaje vacÃ­o"}, status=400)

    if not session_id:
        return JsonResponse({"error": "session_id requerido"}, status=400)

    try:
        logger.debug(
            "Chat request: user=%s session=%s msg_len=%d",
            request.user.username,
            session_id[:8],
            len(user_message),
        )
        result = process_message(request.user, user_message, session_id)
        return JsonResponse(result)
    except Exception as exc:
        logger.error("Chat error for user %s: %s", request.user.id, exc)
        return JsonResponse(
            {
                "response": "Lo siento, hubo un error interno. Por favor, intenta de nuevo.",
                "is_followup": False,
                "followup_options": None,
                "session_id": session_id,
            }
        )


@login_required
@require_GET
def get_conversation_history(request):
    session_id = request.GET.get("session_id", "").strip()

    if not session_id:
        return JsonResponse({"error": "session_id requerido"}, status=400)

    messages = ConversationMessage.objects.filter(
        usuario=request.user,
        session_id=session_id,
    ).order_by("created_at")

    return JsonResponse(
        {
            "messages": [
                {
                    "role": message.role,
                    "content": message.content,
                    "is_followup": message.is_followup_question,
                    "timestamp": message.created_at.isoformat(),
                }
                for message in messages
            ],
            "session_id": session_id,
        }
    )


@login_required
@require_POST
def start_new_conversation(request):
    return JsonResponse({"status": "ok"})

