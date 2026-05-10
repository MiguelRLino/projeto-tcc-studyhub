from rest_framework.authentication import BaseAuthentication

from apps.alunos.models import Aluno
from apps.alunos.services.auth_service import decodificar_token


class JWTAuthentication(BaseAuthentication):
    """Lê `Authorization: Bearer <token>` e anexa o `Aluno` em `request.user`."""

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
        # Inválido/expirado: não levanta erro — vira anônimo (permite login/cadastro com header velho no cliente).
        if not payload or "id_aluno" not in payload:
            return None

        try:
            aluno = Aluno.objects.get(pk=payload["id_aluno"])
        except Aluno.DoesNotExist:
            return None

        # Compatível com `IsAuthenticated` do DRF
        aluno.is_authenticated = True  # type: ignore[attr-defined]
        return aluno, token
