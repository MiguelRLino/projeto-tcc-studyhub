from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from apps.alunos.models import Aluno


class AlunoCadastroSerializer(serializers.ModelSerializer):
    """Cadastro: senha em texto na requisição; persistência apenas com hash."""

    senha = serializers.CharField(write_only=True, min_length=8, max_length=128)

    class Meta:
        model = Aluno
        fields = ("nome", "email", "senha")

    def validate_nome(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Nome é obrigatório.")
        return value

    def validate_email(self, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError("E-mail é obrigatório.")
        if Aluno.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Este e-mail já está cadastrado.")
        return value

    def create(self, validated_data):
        senha_plana = validated_data.pop("senha")
        validated_data["senha"] = make_password(senha_plana)
        return super().create(validated_data)


class AlunoLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    senha = serializers.CharField(required=True, write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = (attrs.get("email") or "").strip().lower()
        senha = attrs.get("senha")
        if not email:
            raise serializers.ValidationError({"email": "E-mail é obrigatório."})
        if not senha:
            raise serializers.ValidationError({"senha": "Senha é obrigatória."})
        attrs["email"] = email
        return attrs


class AlunoGoogleCredentialSerializer(serializers.Serializer):
    """JWT (`credential`) emitido pelo Google Identity Services no frontend."""

    credential = serializers.CharField(required=True, write_only=True, trim_whitespace=False)


class AlunoPublicoSerializer(serializers.ModelSerializer):
    """Dados seguros do aluno (sem senha)."""

    class Meta:
        model = Aluno
        fields = ("id_aluno", "nome", "email")
