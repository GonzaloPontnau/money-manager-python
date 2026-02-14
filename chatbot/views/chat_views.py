import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from chatbot.models.conversation import ConversationMessage
from chatbot.services.rag_pipeline import process_message

logger = logging.getLogger(__name__)


@login_required
@require_POST
def send_message(request):
    """Main chat endpoint. Receives user message, returns AI response."""
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    user_message = body.get('message', '').strip()
    session_id = body.get('session_id', '').strip()

    if not user_message:
        return JsonResponse({'error': 'Mensaje vacío'}, status=400)

    if not session_id:
        return JsonResponse({'error': 'session_id requerido'}, status=400)

    try:
        logger.debug("Chat request: user=%s session=%s msg_len=%d", request.user.username, session_id[:8], len(user_message))
        result = process_message(request.user, user_message, session_id)
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Chat error for user {request.user.id}: {e}")
        return JsonResponse({
            'response': 'Lo siento, hubo un error interno. Por favor, intenta de nuevo.',
            'is_followup': False,
            'followup_options': None,
            'session_id': session_id,
        })


@login_required
@require_GET
def get_conversation_history(request):
    """Load conversation history for a given session."""
    session_id = request.GET.get('session_id', '').strip()

    if not session_id:
        return JsonResponse({'error': 'session_id requerido'}, status=400)

    messages = ConversationMessage.objects.filter(
        usuario=request.user,
        session_id=session_id,
    ).order_by('created_at').values('role', 'content', 'is_followup_question', 'created_at')

    return JsonResponse({
        'messages': [
            {
                'role': m['role'],
                'content': m['content'],
                'is_followup': m['is_followup_question'],
                'timestamp': m['created_at'].isoformat(),
            }
            for m in messages
        ],
        'session_id': session_id,
    })


@login_required
@require_POST
def start_new_conversation(request):
    """Start a new conversation session."""
    return JsonResponse({'status': 'ok'})
