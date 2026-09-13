from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.telegram.conexao_service import (
    CODIGO_TTL_MINUTOS,
    desconectar_telegram,
    gerar_codigo_conexao,
    obter_ou_criar_config,
    registrar_log_telegram,
)
from apps.telegram.models import ConfiguracaoTelegram
from apps.telegram.serializers import (
    CodigoConexaoSerializer,
    ConfiguracaoTelegramReadSerializer,
    ConfiguracaoTelegramUpdateSerializer,
    serializar_config_aluno,
)


class TelegramConfiguracaoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(serializar_config_aluno(request.user))

    def patch(self, request):
        config = obter_ou_criar_config(request.user)
        serializer = ConfiguracaoTelegramUpdateSerializer(
            config, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ConfiguracaoTelegramReadSerializer(config).data)


class TelegramGerarCodigoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        registro = gerar_codigo_conexao(request.user)
        return Response(
            {
                "codigo": registro.codigo,
                "expira_em_minutos": CODIGO_TTL_MINUTOS,
            },
            status=status.HTTP_201_CREATED,
        )


class TelegramDesconectarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        config = ConfiguracaoTelegram.objects.filter(
            aluno=request.user, data_exclusao__isnull=True
        ).first()
        desconectar_telegram(request.user)
        if config:
            registrar_log_telegram(
                request.user,
                "TELEGRAM_DESCONECTADO",
                "Aluno desconectou o Telegram do StudyHub.",
                id_registro_afetado=config.pk,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
