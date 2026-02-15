from django.contrib.auth.models import User
from rest_framework import serializers

from chatbot.models import ConversationMessage
from finanzas.models import Categoria, Transaccion, Transferencia


class TransactionSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = Transaccion
        fields = [
            "id",
            "fecha",
            "monto",
            "tipo",
            "categoria",
            "categoria_nombre",
            "descripcion",
            "comprobante",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_actualizacion"]

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor que cero.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        tipo = attrs.get("tipo", getattr(self.instance, "tipo", None))
        categoria = attrs.get("categoria", getattr(self.instance, "categoria", None))

        if categoria and categoria.usuario_id != request.user.id:
            raise serializers.ValidationError(
                {"categoria": "La categoria seleccionada no pertenece al usuario autenticado."}
            )

        if tipo and categoria and categoria.tipo != tipo:
            raise serializers.ValidationError(
                {"categoria": "El tipo de la categoria debe coincidir con el tipo de transaccion."}
            )

        return attrs

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)


class TransferSerializer(serializers.ModelSerializer):
    emisor = serializers.CharField(source="emisor.username", read_only=True)
    receptor = serializers.CharField(source="receptor.username", read_only=True)

    class Meta:
        model = Transferencia
        fields = [
            "uuid",
            "emisor",
            "receptor",
            "monto",
            "concepto",
            "estado",
            "referencia",
            "codigo_respuesta",
            "mensaje_respuesta",
            "fecha_creacion",
            "fecha_procesamiento",
        ]
        read_only_fields = fields


class TransferCreateSerializer(serializers.Serializer):
    receptor_username = serializers.CharField(max_length=150)
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)
    concepto = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor que cero.")
        return value

    def validate_receptor_username(self, value):
        request = self.context["request"]
        try:
            receptor = User.objects.get(username=value)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError("Este usuario no existe en el sistema.") from exc

        if receptor.id == request.user.id:
            raise serializers.ValidationError("No puedes transferir dinero a ti mismo.")
        return value


class ChatSessionSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=64)
    updated_at = serializers.DateTimeField()


class ChatMessageSerializer(serializers.ModelSerializer):
    is_followup = serializers.BooleanField(source="is_followup_question", read_only=True)
    timestamp = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = ConversationMessage
        fields = ["role", "content", "is_followup", "timestamp"]


class ChatSendSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=64)
    message = serializers.CharField()
