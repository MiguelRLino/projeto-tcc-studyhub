from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers

from apps.alunos.models import Aluno
from apps.alunos.services.senha_validator import mensagem_erro_senha


def _validar_campo_senha(value: str, field_name: str = "senha") -> str:
    msg = mensagem_erro_senha(value or "")
    if msg:
        raise serializers.ValidationError({field_name: msg})
    return value


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

    def validate_senha(self, value: str) -> str:
        return _validar_campo_senha(value, "senha")

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


class AlunoPerfilUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ("nome",)

    def validate_nome(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Nome é obrigatório.")
        return value


class AlunoRecuperarSenhaSolicitarSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        return value.strip().lower()


class AlunoRecuperarSenhaConfirmarSerializer(serializers.Serializer):
    token = serializers.CharField()
    senha_nova = serializers.CharField(min_length=8, max_length=128, write_only=True)

    def validate_senha_nova(self, value: str) -> str:
        return _validar_campo_senha(value, "senha_nova")


class AlunoAlterarSenhaSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(write_only=True, trim_whitespace=False)
    senha_nova = serializers.CharField(write_only=True, min_length=8, max_length=128)

    def validate(self, attrs):
        aluno = self.context["request"].user
        if not check_password(attrs["senha_atual"], aluno.senha):
            raise serializers.ValidationError(
                {"senha_atual": "Senha atual incorreta."}
            )
        _validar_campo_senha(attrs.get("senha_nova", ""), "senha_nova")
        return attrs
