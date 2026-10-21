from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from apps.alunos.models import Aluno
from apps.alunos.services.auth_service import TIPO_RESPONSAVEL, criar_token_acesso
from apps.responsaveis.dashboard_service import (
    listar_disciplinas,
    listar_sessoes,
    listar_tarefas,
    montar_dashboard,
    montar_relatorios,
)
from apps.responsaveis.models import Responsavel, ResponsavelAluno, StatusVinculo
from apps.responsaveis.permissions import IsAluno, IsResponsavel, vinculo_ativo
from apps.responsaveis.serializers import (
    AceitarConviteSerializer,
    ConvidarResponsavelSerializer,
)
from apps.responsaveis.services import (
    ConviteErro,
    aceitar_convite,
    cancelar_convite,
    convidar_responsavel,
    listar_meus_responsaveis,
    reenviar_convite,
    remover_vinculo,
    validar_convite_publico,
)


class ConviteThrottle(AnonRateThrottle):
    rate = "20/hour"


class ConviteUserThrottle(UserRateThrottle):
    rate = "30/hour"


class ConvidarResponsavelAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAluno]
    throttle_classes = [ConviteUserThrottle]

    def post(self, request):
        serializer = ConvidarResponsavelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            convite, link_dev = convidar_responsavel(
                request.user,
                nome=serializer.validated_data["nome"],
                email=serializer.validated_data["email"],
                parentesco=serializer.validated_data["parentesco"],
            )
        except ConviteErro as exc:
            return Response(
                {"erro": exc.mensagem},
                status=exc.status_code,
            )
        payload = {
            "mensagem": "Convite enviado com sucesso.",
            "convite": {
                "id": convite.id_convite,
                "nome": convite.nome_convidado,
                "email": convite.email_convidado,
                "parentesco": convite.parentesco,
                "status": convite.status,
            },
        }
        if link_dev:
            payload["link_desenvolvimento"] = link_dev
        return Response(payload, status=status.HTTP_201_CREATED)


class MeusResponsaveisAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAluno]

    def get(self, request):
        return Response({"itens": listar_meus_responsaveis(request.user)})


class ReenviarConviteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAluno]
    throttle_classes = [ConviteUserThrottle]

    def post(self, request, convite_id: int):
        try:
            convite, link_dev = reenviar_convite(request.user, convite_id)
        except ConviteErro as exc:
            return Response({"erro": exc.mensagem}, status=exc.status_code)
        payload = {
            "mensagem": "Convite reenviado com sucesso.",
            "convite": {
                "id": convite.id_convite,
                "email": convite.email_convidado,
                "status": convite.status,
            },
        }
        if link_dev:
            payload["link_desenvolvimento"] = link_dev
        return Response(payload)


class CancelarConviteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAluno]

    def delete(self, request, convite_id: int):
        try:
            cancelar_convite(request.user, convite_id)
        except ConviteErro as exc:
            return Response({"erro": exc.mensagem}, status=exc.status_code)
        return Response({"mensagem": "Convite cancelado."})


class RemoverVinculoAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAluno]

    def delete(self, request, vinculo_id: int):
        try:
            remover_vinculo(request.user, vinculo_id)
        except ConviteErro as exc:
            return Response({"erro": exc.mensagem}, status=exc.status_code)
        return Response({"mensagem": "Responsável removido com sucesso."})


class ValidarConviteAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ConviteThrottle]

    def get(self, request, token: str):
        try:
            data = validar_convite_publico(token)
        except ConviteErro as exc:
            return Response({"erro": exc.mensagem}, status=exc.status_code)
        return Response(data)


class AceitarConviteAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ConviteThrottle]

    def post(self, request):
        serializer = AceitarConviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        responsavel_auth = None
        user = request.user
        if (
            getattr(user, "is_authenticated", False)
            and isinstance(user, Responsavel)
        ):
            responsavel_auth = user

        try:
            result = aceitar_convite(
                token,
                senha=serializer.validated_data.get("senha") or None,
                senha_confirmacao=serializer.validated_data.get("senha_confirmacao")
                or None,
                responsavel_autenticado=responsavel_auth,
            )
        except ConviteErro as exc:
            return Response({"erro": exc.mensagem}, status=exc.status_code)
        return Response(result, status=status.HTTP_200_OK)


class MeusAlunosAPIView(APIView):
    permission_classes = [IsAuthenticated, IsResponsavel]

    def get(self, request):
        vinculos = (
            ResponsavelAluno.objects.filter(
                responsavel=request.user,
                status=StatusVinculo.ATIVO,
                data_exclusao__isnull=True,
            )
            .select_related("aluno")
            .order_by("aluno__nome")
        )
        return Response(
            {
                "alunos": [
                    {
                        "vinculo_id": v.id_vinculo,
                        "id_aluno": v.aluno_id,
                        "nome": v.aluno.nome,
                        "email": v.aluno.email,
                        "parentesco": v.parentesco,
                        "data_aceitacao": v.data_aceitacao,
                    }
                    for v in vinculos
                ]
            }
        )


class _AlunoAutorizadoMixin:
    def _aluno_autorizado(self, request, aluno_id: int) -> Aluno | Response:
        vinculo = vinculo_ativo(request.user, aluno_id)
        if not vinculo:
            return Response(
                {"erro": "Você não tem acesso a este aluno."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return vinculo.aluno


class ResponsavelAlunoDashboardAPIView(_AlunoAutorizadoMixin, APIView):
    permission_classes = [IsAuthenticated, IsResponsavel]

    def get(self, request, aluno_id: int):
        aluno = self._aluno_autorizado(request, aluno_id)
        if isinstance(aluno, Response):
            return aluno
        return Response(montar_dashboard(aluno))


class ResponsavelAlunoTarefasAPIView(_AlunoAutorizadoMixin, APIView):
    permission_classes = [IsAuthenticated, IsResponsavel]

    def get(self, request, aluno_id: int):
        aluno = self._aluno_autorizado(request, aluno_id)
        if isinstance(aluno, Response):
            return aluno
        return Response({"tarefas": listar_tarefas(aluno)})


class ResponsavelAlunoDisciplinasAPIView(_AlunoAutorizadoMixin, APIView):
    permission_classes = [IsAuthenticated, IsResponsavel]

    def get(self, request, aluno_id: int):
        aluno = self._aluno_autorizado(request, aluno_id)
        if isinstance(aluno, Response):
            return aluno
        return Response({"disciplinas": listar_disciplinas(aluno)})


class ResponsavelAlunoSessoesAPIView(_AlunoAutorizadoMixin, APIView):
    permission_classes = [IsAuthenticated, IsResponsavel]

    def get(self, request, aluno_id: int):
        aluno = self._aluno_autorizado(request, aluno_id)
        if isinstance(aluno, Response):
            return aluno
        return Response(listar_sessoes(aluno))


class ResponsavelAlunoRelatoriosAPIView(_AlunoAutorizadoMixin, APIView):
    permission_classes = [IsAuthenticated, IsResponsavel]

    def get(self, request, aluno_id: int):
        aluno = self._aluno_autorizado(request, aluno_id)
        if isinstance(aluno, Response):
            return aluno
        return Response(montar_relatorios(aluno))


class ResponsavelLoginAPIView(APIView):
    """Login dedicado (opcional). O login unificado em /api/alunos/login/ também cobre."""

    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        senha = request.data.get("senha") or ""
        if not email or not senha:
            return Response(
                {"erro": "Informe e-mail e senha."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            responsavel = Responsavel.objects.get(email__iexact=email)
        except Responsavel.DoesNotExist:
            return Response(
                {"erro": "E-mail ou senha incorretos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not check_password(senha, responsavel.senha):
            return Response(
                {"erro": "E-mail ou senha incorretos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token = criar_token_acesso(
            tipo=TIPO_RESPONSAVEL,
            id_responsavel=responsavel.id_responsavel,
        )
        return Response(
            {
                "mensagem": "Login realizado com sucesso.",
                "tipo": TIPO_RESPONSAVEL,
                "usuario": {
                    "id_responsavel": responsavel.id_responsavel,
                    "nome": responsavel.nome,
                    "email": responsavel.email,
                },
                "access": token,
            }
        )
