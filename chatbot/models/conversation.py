from django.db import models
from django.contrib.auth.models import User


class ConversationMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('assistant', 'Asistente'),
        ('system', 'Sistema'),
    ]

    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    session_id = models.CharField(
        max_length=64, db_index=True,
        help_text="Agrupa mensajes en conversaciones"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    is_followup_question = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
