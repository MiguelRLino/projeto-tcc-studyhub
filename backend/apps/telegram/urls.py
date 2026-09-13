from django.urls import path

from apps.telegram.views import (
    TelegramConfiguracaoAPIView,
    TelegramDesconectarAPIView,
    TelegramGerarCodigoAPIView,
)

urlpatterns = [
    path(
        "telegram/configuracao/",
        TelegramConfiguracaoAPIView.as_view(),
        name="telegram-configuracao",
    ),
    path(
        "telegram/gerar-codigo/",
        TelegramGerarCodigoAPIView.as_view(),
        name="telegram-gerar-codigo",
    ),
    path(
        "telegram/desconectar/",
        TelegramDesconectarAPIView.as_view(),
        name="telegram-desconectar",
    ),
]
