"""Querysets reutilizáveis com métricas agregadas."""

from decimal import Decimal

from django.db.models import (
    Count,
    DecimalField,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce

from apps.sistema_estudos.models import Disciplina, SessaoEstudo, Tarefa


def tarefas_concluidas_q() -> Q:
    return (
        Q(status_tarefa__iexact="concluida")
        | Q(status_tarefa__iexact="concluída")
        | Q(status_tarefa__iexact="concluido")
        | Q(status_tarefa__iexact="concluído")
        | Q(status_tarefa__iexact="feito")
        | Q(status_tarefa__iexact="done")
    )


def disciplinas_ativas_com_metricas(aluno):
    """
    Disciplinas não excluídas do aluno com:
    - horas_estudadas: soma de `sessao_estudo.tempo_estudo` (sessões ativas)
    - tarefas_pendentes: tarefas ativas cuja situação não é “concluída”
    """
    cq = tarefas_concluidas_q()

    horas_sq = (
        SessaoEstudo.objects.filter(
            disciplina_id=OuterRef("id_disciplina"),
            data_exclusao__isnull=True,
        )
        .values("disciplina_id")
        .annotate(total=Sum("tempo_estudo"))
        .values("total")[:1]
    )

    pend_sq = (
        Tarefa.objects.filter(
            disciplina_id=OuterRef("id_disciplina"),
            data_exclusao__isnull=True,
        )
        .exclude(cq)
        .values("disciplina_id")
        .annotate(cnt=Count("id_tarefa"))
        .values("cnt")[:1]
    )

    return (
        Disciplina.objects.filter(aluno=aluno, data_exclusao__isnull=True)
        .annotate(
            horas_estudadas=Coalesce(
                Subquery(
                    horas_sq,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                Value(Decimal("0")),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            tarefas_pendentes=Coalesce(
                Subquery(pend_sq, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            ),
        )
        .order_by("nome")
    )
