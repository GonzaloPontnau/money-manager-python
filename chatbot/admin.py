from django.contrib import admin

from chatbot.models import ConversationMessage


@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ("usuario", "session_id", "role", "is_followup_question", "created_at")
    search_fields = ("usuario__username", "session_id", "content")
    list_filter = ("role", "is_followup_question", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

