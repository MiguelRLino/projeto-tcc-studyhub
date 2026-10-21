from rest_framework.authentication import BaseAuthentication

from apps.alunos.models import Aluno
from apps.alunos.services.auth_service import (
    TIPO_ALUNO,
    TIPO_RESPONSAVEL,
    decodificar_token,
)


class JWTAuthentication(BaseAuthentication):
    """Lê `Authorization: Bearer <token>` e anexa Aluno ou Responsavel em `request.user`."""

    keyword = b"Bearer"

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION")
        if not header:
            return None
        try:
            scheme, token = header.split(None, 1)
        except ValueError:
            return None
        if scheme.lower() != "bearer":
            return None
        token = token.strip()
        if not token:
            return None

        payload = decodificar_token(token)
        if not payload:
            return None

        tipo = payload.get("tipo") or TIPO_ALUNO

        if tipo == TIPO_RESPONSAVEL:
            id_resp = payload.get("id_responsavel")
            if not id_resp:
                return None
            from apps.responsaveis.models import Responsavel

            try:
                responsavel = Responsavel.objects.get(pk=id_resp)
            except Responsavel.DoesNotExist:
                return None
            responsavel.is_authenticated = True  # type: ignore[attr-defined]
            responsavel.tipo_usuario = TIPO_RESPONSAVEL  # type: ignore[attr-defined]
            return responsavel, token

        # ALUNO (tokens antigos sem claim `tipo` continuam válidos)
        if "id_aluno" not in payload:
            return None
        try:
            aluno = Aluno.objects.get(pk=payload["id_aluno"])
        except Aluno.DoesNotExist:
            return None
        aluno.is_authenticated = True  # type: ignore[attr-defined]
        aluno.tipo_usuario = TIPO_ALUNO  # type: ignore[attr-defined]
        return aluno, token
