from rest_framework import serializers

from apps.telegram.conexao_service import CODIGO_TTL_MINUTOS, obter_ou_criar_config
from apps.telegram.models import ConfiguracaoTelegram


class ConfiguracaoTelegramReadSerializer(serializers.ModelSerializer):
    conectado = serializers.SerializerMethodField()
    bot_username = serializers.SerializerMethodField()

    class Meta:
        model = ConfiguracaoTelegram
        fields = (
            "conectado",
            "telegram_username",
            "telegram_ativo",
            "notificar_24h",
            "notificar_2h",
            "bot_username",
        )

    def get_conectado(self, obj):
        return bool(obj.telegram_ativo and obj.telegram_chat_id)

    def get_bot_username(self, obj):
        from django.conf import settings

        return getattr(settings, "TELEGRAM_BOT_USERNAME", "").strip()


class ConfiguracaoTelegramUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoTelegram
        fields = ("telegram_ativo", "notificar_24h", "notificar_2h")

    def update(self, instance, validated_data):
        if not instance.telegram_chat_id and validated_data.get("telegram_ativo"):
            raise serializers.ValidationError(
                {"telegram_ativo": "Conecte o Telegram antes de ativar notificações."}
            )
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class CodigoConexaoSerializer(serializers.Serializer):
    codigo = serializers.CharField(read_only=True)
    expira_em_minutos = serializers.IntegerField(read_only=True)

    @staticmethod
    def from_registro(registro):
        return {
            "codigo": registro.codigo,
            "expira_em_minutos": CODIGO_TTL_MINUTOS,
        }


def serializar_config_aluno(aluno):
    config = obter_ou_criar_config(aluno)
    return ConfiguracaoTelegramReadSerializer(config).data
