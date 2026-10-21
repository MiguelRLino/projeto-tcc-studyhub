from rest_framework.permissions import BasePermission

from apps.alunos.models import Aluno
from apps.responsaveis.models import Responsavel, ResponsavelAluno, StatusVinculo


class IsAluno(BasePermission):
    message = "Acesso restrito a alunos."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and getattr(user, "is_authenticated", False)
            and isinstance(user, Aluno)
            and getattr(user, "tipo_usuario", "ALUNO") == "ALUNO"
        )


class IsResponsavel(BasePermission):
    message = "Acesso restrito a responsáveis."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and getattr(user, "is_authenticated", False)
            and isinstance(user, Responsavel)
            and getattr(user, "tipo_usuario", "RESPONSAVEL") == "RESPONSAVEL"
        )


def vinculo_ativo(responsavel: Responsavel, aluno_id: int) -> ResponsavelAluno | None:
    return (
        ResponsavelAluno.objects.filter(
            responsavel=responsavel,
            aluno_id=aluno_id,
            status=StatusVinculo.ATIVO,
            data_exclusao__isnull=True,
        )
        .select_related("aluno")
        .first()
    )
