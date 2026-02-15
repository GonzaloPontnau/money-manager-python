from django.urls import path

from chatbot.views import (
    get_conversation_history,
    send_message,
    start_new_conversation,
)

app_name = "chatbot"

urlpatterns = [
    path("api/chat/send/", send_message, name="send_message"),
    path("api/chat/history/", get_conversation_history, name="history"),
    path("api/chat/new/", start_new_conversation, name="new_conversation"),
]

