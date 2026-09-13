from django.urls import path

from apps.assistente_ia.views import (
    AssistenteHistoricoDetailAPIView,
    AssistenteHistoricoListAPIView,
    AssistentePerguntarAPIView,
)

urlpatterns = [
    path(
        "assistente/perguntar/",
        AssistentePerguntarAPIView.as_view(),
        name="assistente-perguntar",
    ),
    path(
        "assistente/historico/",
        AssistenteHistoricoListAPIView.as_view(),
        name="assistente-historico",
    ),
    path(
        "assistente/historico/<int:pk>/",
        AssistenteHistoricoDetailAPIView.as_view(),
        name="assistente-historico-detail",
    ),
]
