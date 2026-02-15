import uuid

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Max, Q, Sum
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.v1.serializers import (
    ChatMessageSerializer,
    ChatSendSerializer,
    ChatSessionSerializer,
    TransactionSerializer,
    TransferCreateSerializer,
    TransferSerializer,
)
from chatbot.models import ConversationMessage
from chatbot.services.rag_pipeline import process_message
from finanzas.models import Categoria, Transaccion, Transferencia
from finanzas.views import _build_dashboard_payload


class AuthLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class AuthRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class AuthLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id="v1_auth_logout",
        request=None,
        responses={204: OpenApiResponse(description="Logged out")},
    )
    def post(self, request):
        # JWT logout is stateless unless token blacklisting is enabled.
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id="v1_dashboard_summary",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        return Response(_build_dashboard_payload(request.user))


class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Transaccion.objects.filter(usuario=self.request.user)
            .select_related("categoria")
            .order_by("-fecha")
        )


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Transaccion.objects.filter(usuario=self.request.user).select_related("categoria")


class TransferListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id="v1_transfers_list",
        responses={200: TransferSerializer(many=True)},
    )
    def get(self, request):
        queryset = (
            Transferencia.objects.filter(Q(emisor=request.user) | Q(receptor=request.user))
            .select_related("emisor", "receptor")
            .order_by("-fecha_creacion")
        )
        return Response(TransferSerializer(queryset, many=True).data)

    @extend_schema(
        operation_id="v1_transfers_create",
        request=TransferCreateSerializer,
        responses={201: TransferSerializer, 400: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        serializer = TransferCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        receptor_username = serializer.validated_data["receptor_username"]
        monto = serializer.validated_data["monto"]
        concepto = serializer.validated_data.get("concepto", "")

        receptor = User.objects.get(username=receptor_username)
        emisor = request.user

        with transaction.atomic():
            lock_ids = sorted({emisor.id, receptor.id})
            locked_users = {
                user.id: user
                for user in User.objects.select_for_update().filter(id__in=lock_ids).order_by("id")
            }
            emisor_locked = locked_users[emisor.id]
            receptor_locked = locked_users[receptor.id]

            ingresos = (
                Transaccion.objects.filter(usuario=emisor_locked, tipo="ingreso")
                .aggregate(total=Sum("monto"))["total"]
                or 0
            )
            gastos = (
                Transaccion.objects.filter(usuario=emisor_locked, tipo="gasto")
                .aggregate(total=Sum("monto"))["total"]
                or 0
            )
            saldo_actual = ingresos - gastos

            if saldo_actual < monto:
                return Response(
                    {"detail": f"No tienes saldo suficiente. Tu saldo actual es: {saldo_actual}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            transferencia = Transferencia.objects.create(
                emisor=emisor_locked,
                receptor=receptor_locked,
                monto=monto,
                concepto=concepto,
            )

            categoria_gasto = (
                Categoria.objects.filter(
                    usuario=emisor_locked,
                    tipo="gasto",
                    nombre="Transferencia enviada",
                ).first()
                or Categoria.objects.filter(usuario=emisor_locked, tipo="gasto").first()
            )
            categoria_ingreso = (
                Categoria.objects.filter(
                    usuario=receptor_locked,
                    tipo="ingreso",
                    nombre="Transferencia recibida",
                ).first()
                or Categoria.objects.filter(usuario=receptor_locked, tipo="ingreso").first()
            )

            Transaccion.objects.create(
                usuario=emisor_locked,
                monto=monto,
                tipo="gasto",
                categoria=categoria_gasto,
                descripcion=f"Transferencia a {receptor_locked.username}: {concepto}",
            )
            Transaccion.objects.create(
                usuario=receptor_locked,
                monto=monto,
                tipo="ingreso",
                categoria=categoria_ingreso,
                descripcion=f"Transferencia de {emisor_locked.username}: {concepto}",
            )

            transferencia.completar()

        return Response(TransferSerializer(transferencia).data, status=status.HTTP_201_CREATED)


class TransferDetailView(generics.RetrieveAPIView):
    serializer_class = TransferSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        return Transferencia.objects.filter(
            Q(emisor=self.request.user) | Q(receptor=self.request.user)
        ).select_related("emisor", "receptor")


class TransferCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id="v1_transfer_cancel",
        request=None,
        responses={200: TransferSerializer, 400: OpenApiTypes.OBJECT},
    )
    def post(self, request, uuid):
        transferencia = generics.get_object_or_404(
            Transferencia.objects.select_related("emisor", "receptor"),
            uuid=uuid,
            emisor=request.user,
        )

        if transferencia.estado != "pending":
            return Response(
                {"detail": "Solo se pueden cancelar transferencias pendientes."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transferencia.cancelar()
        return Response(TransferSerializer(transferencia).data)


class ChatSessionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id="v1_chat_sessions_list",
        responses={200: ChatSessionSerializer(many=True)},
    )
    def get(self, request):
        sessions = (
            ConversationMessage.objects.filter(usuario=request.user)
            .values("session_id")
            .annotate(updated_at=Max("created_at"))
            .order_by("-updated_at")
        )
        return Response(ChatSessionSerializer(sessions, many=True).data)

    @extend_schema(
        operation_id="v1_chat_sessions_create",
        request=None,
        responses={201: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        session_id = f"chat_{uuid.uuid4().hex[:12]}"
        return Response({"session_id": session_id}, status=status.HTTP_201_CREATED)


class ChatSendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id="v1_chat_messages_send",
        request=ChatSendSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        serializer = ChatSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_id = serializer.validated_data["session_id"]
        message = serializer.validated_data["message"].strip()
        if not message:
            return Response({"detail": "Mensaje vacio."}, status=status.HTTP_400_BAD_REQUEST)

        result = process_message(request.user, message, session_id)
        return Response(result)


class ChatSessionMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id="v1_chat_session_messages",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request, session_id):
        messages = ConversationMessage.objects.filter(
            usuario=request.user,
            session_id=session_id,
        ).order_by("created_at")
        return Response(
            {
                "session_id": session_id,
                "messages": ChatMessageSerializer(messages, many=True).data,
            }
        )
