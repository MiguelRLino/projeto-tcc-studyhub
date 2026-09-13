"""Registro de atividades do Caderno Digital."""

from django.utils import timezone

from apps.sistema_estudos.models import LogAtividade


def registrar_log_caderno(
    aluno,
    acao: str,
    descricao: str,
    *,
    tabela_afetada: str = "caderno",
    id_registro_afetado: int | None = None,
) -> None:
    LogAtividade.objects.create(
        aluno=aluno,
        acao=acao,
        tabela_afetada=tabela_afetada,
        id_registro_afetado=id_registro_afetado,
        descricao=descricao[:255],
        data_hora=timezone.now(),
    )
