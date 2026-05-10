import secrets

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.alunos.models import Aluno
from apps.alunos.serializers import (
    AlunoCadastroSerializer,
    AlunoGoogleCredentialSerializer,
    AlunoLoginSerializer,
    AlunoPublicoSerializer,
)
from apps.alunos.services.auth_service import criar_token_acesso


class AlunoCadastroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AlunoCadastroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        aluno = serializer.save()
        token = criar_token_acesso(aluno.id_aluno)
        return Response(
            {
                "mensagem": "Cadastro realizado com sucesso.",
                "aluno": AlunoPublicoSerializer(aluno).data,
                "access": token,
            },
            status=status.HTTP_201_CREATED,
        )


class AlunoLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AlunoLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        senha = serializer.validated_data["senha"]

        try:
            aluno = Aluno.objects.get(email__iexact=email)
        except Aluno.DoesNotExist:
            return Response(
                {"erro": "E-mail ou senha incorretos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_password(senha, aluno.senha):
            return Response(
                {"erro": "E-mail ou senha incorretos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = criar_token_acesso(aluno.id_aluno)
        return Response(
            {
                "mensagem": "Login realizado com sucesso.",
                "aluno": AlunoPublicoSerializer(aluno).data,
                "access": token,
            },
            status=status.HTTP_200_OK,
        )


class AlunoGoogleLoginView(APIView):
    """Login opcional com Google (cria conta na primeira vez se o e-mail ainda não existir)."""

    permission_classes = [AllowAny]

    def post(self, request):
        if not getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", ""):
            return Response(
                {
                    "erro": "Login Google não configurado no servidor. Defina GOOGLE_OAUTH_CLIENT_ID no .env.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        serializer = AlunoGoogleCredentialSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        credential = serializer.validated_data["credential"]

        try:
            from google.auth.transport import requests as google_requests
            from google.oauth2 import id_token

            idinfo = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                settings.GOOGLE_OAUTH_CLIENT_ID,
            )
        except ValueError:
            return Response(
                {"erro": "Credencial Google inválida ou expirada. Tente novamente."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        iss = idinfo.get("iss")
        if iss not in ("accounts.google.com", "https://accounts.google.com"):
            return Response(
                {"erro": "Token com origem inválida."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email = (idinfo.get("email") or "").strip().lower()
        if not email:
            return Response(
                {"erro": "Sua conta Google não retornou um e-mail."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not idinfo.get("email_verified"):
            return Response(
                {"erro": "Confirme o e-mail na sua conta Google antes de entrar."},
                status=status.HTTP_403_FORBIDDEN,
            )

        nome_google = (idinfo.get("name") or "").strip()
        nome = (nome_google or email.split("@")[0])[:100]

        try:
            aluno = Aluno.objects.get(email__iexact=email)
            if (not (aluno.nome or "").strip()) and nome:
                aluno.nome = nome
                aluno.save(update_fields=["nome"])
        except Aluno.DoesNotExist:
            aluno = Aluno.objects.create(
                nome=nome,
                email=email,
                senha=make_password(secrets.token_urlsafe(64)),
            )

        token = criar_token_acesso(aluno.id_aluno)
        return Response(
            {
                "mensagem": "Login realizado com sucesso.",
                "aluno": AlunoPublicoSerializer(aluno).data,
                "access": token,
            },
            status=status.HTTP_200_OK,
        )


class AlunoPerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        aluno = request.user
        return Response(AlunoPublicoSerializer(aluno).data, status=status.HTTP_200_OK)
