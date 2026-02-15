from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chatbot"
    verbose_name = "Chatbot Financiero"

    def ready(self):
        # Register optional signals for transaction embeddings.
        try:
            import chatbot.signals  # noqa: F401
        except Exception:
            # Keep app boot resilient when optional integrations are unavailable.
            pass

