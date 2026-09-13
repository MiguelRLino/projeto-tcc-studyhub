from rest_framework import serializers

from apps.assistente_ia.models import ConversaIA
from apps.assistente_ia.services import PERGUNTA_MAX_CARACTERES


class PerguntaSerializer(serializers.Serializer):
    pergunta = serializers.CharField(
        max_length=PERGUNTA_MAX_CARACTERES,
        trim_whitespace=True,
        allow_blank=True,
    )

    def validate_pergunta(self, value):
        if not (value or "").strip():
            raise serializers.ValidationError("Informe sua pergunta.")
        return value.strip()


class ConversaReadSerializer(serializers.ModelSerializer):
    titulo = serializers.SerializerMethodField()

    class Meta:
        model = ConversaIA
        fields = (
            "id_conversa",
            "titulo",
            "pergunta",
            "resposta",
            "data_criacao",
        )

    def get_titulo(self, obj):
        texto = (obj.pergunta or "").strip()
        if len(texto) <= 60:
            return texto or "Consulta"
        return f"{texto[:57]}..."
