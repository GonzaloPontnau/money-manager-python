from django.urls import path

from api.v1.views import (
    AuthLoginView,
    AuthLogoutView,
    AuthRefreshView,
    ChatSendView,
    ChatSessionMessagesView,
    ChatSessionsView,
    DashboardSummaryView,
    TransactionDetailView,
    TransactionListCreateView,
    TransferCancelView,
    TransferDetailView,
    TransferListCreateView,
)

urlpatterns = [
    path("auth/login", AuthLoginView.as_view(), name="api_v1_auth_login"),
    path("auth/refresh", AuthRefreshView.as_view(), name="api_v1_auth_refresh"),
    path("auth/logout", AuthLogoutView.as_view(), name="api_v1_auth_logout"),
    path("dashboard/summary", DashboardSummaryView.as_view(), name="api_v1_dashboard_summary"),
    path("transactions", TransactionListCreateView.as_view(), name="api_v1_transactions"),
    path("transactions/<int:id>", TransactionDetailView.as_view(), name="api_v1_transaction_detail"),
    path("transfers", TransferListCreateView.as_view(), name="api_v1_transfers"),
    path("transfers/<uuid:uuid>", TransferDetailView.as_view(), name="api_v1_transfer_detail"),
    path("transfers/<uuid:uuid>/cancel", TransferCancelView.as_view(), name="api_v1_transfer_cancel"),
    path("chat/sessions", ChatSessionsView.as_view(), name="api_v1_chat_sessions"),
    path("chat/messages", ChatSendView.as_view(), name="api_v1_chat_messages"),
    path(
        "chat/sessions/<str:session_id>/messages",
        ChatSessionMessagesView.as_view(),
        name="api_v1_chat_session_messages",
    ),
]
