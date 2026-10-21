from rest_framework import serializers

from apps.responsaveis.models import Parentesco


class ConvidarResponsavelSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=150)
    parentesco = serializers.ChoiceField(choices=Parentesco.choices)


class AceitarConviteSerializer(serializers.Serializer):
    token = serializers.CharField()
    senha = serializers.CharField(required=False, allow_blank=True, write_only=True)
    senha_confirmacao = serializers.CharField(
        required=False, allow_blank=True, write_only=True
    )
