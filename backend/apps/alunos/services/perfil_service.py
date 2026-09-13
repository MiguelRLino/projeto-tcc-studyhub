"""Agregações para a tela de perfil do aluno."""

from datetime import timedelta

from django.db.models import Min, Sum
from django.utils import timezone

from apps.assistente_ia.models import ConversaIA
from apps.telegram.models import ConfiguracaoTelegram, NotificacaoTelegram
from apps.cadernos.models import Caderno, ImagemCaderno, PaginaCaderno
from apps.sistema_estudos.models import (
    Disciplina,
    LogAtividade,
    Relatorio,
    SessaoEstudo,
    Sugestao,
    Tarefa,
)
from apps.sistema_estudos.querysets import tarefas_concluidas_q

MESES_PT = (
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
)


def _label_mes_ano(data) -> str:
    if not data:
        return "Conta recente"
    if hasattr(data, "month"):
        return f"{MESES_PT[data.month - 1]} de {data.year}"
    return str(data)


def _membro_desde(aluno):
    log_min = LogAtividade.objects.filter(aluno=aluno).aggregate(m=Min("data_hora"))["m"]
    if log_min:
        return timezone.localtime(log_min).date()
    sess_min = SessaoEstudo.objects.filter(aluno=aluno).aggregate(m=Min("data_sessao"))["m"]
    if sess_min:
        return sess_min
    return timezone.localdate()


def _dias_sequencia(aluno, hoje):
    datas = set(
        SessaoEstudo.objects.filter(
            aluno=aluno,
            data_exclusao__isnull=True,
            data_sessao__isnull=False,
        ).values_list("data_sessao", flat=True)
    )
    streak = 0
    d = hoje
    while d in datas:
        streak += 1
        d -= timedelta(days=1)
    return streak


def excluir_aluno_e_dados(aluno):
    """Remove dados vinculados (FK PROTECT) e depois o aluno."""
    disciplina_ids = list(
        Disciplina.objects.filter(aluno=aluno).values_list("id_disciplina", flat=True)
    )
    if disciplina_ids:
        Tarefa.objects.filter(disciplina_id__in=disciplina_ids).delete()
        SessaoEstudo.objects.filter(disciplina_id__in=disciplina_ids).delete()
    caderno_ids = list(
        Caderno.objects.filter(aluno=aluno).values_list("id_caderno", flat=True)
    )
    if caderno_ids:
        pagina_ids = list(
            PaginaCaderno.objects.filter(caderno_id__in=caderno_ids).values_list(
                "id_pagina", flat=True
            )
        )
        if pagina_ids:
            ImagemCaderno.objects.filter(pagina_id__in=pagina_ids).delete()
        PaginaCaderno.objects.filter(caderno_id__in=caderno_ids).delete()
    Caderno.objects.filter(aluno=aluno).delete()
    ConversaIA.objects.filter(aluno=aluno).delete()
    NotificacaoTelegram.objects.filter(aluno=aluno).delete()
    ConfiguracaoTelegram.objects.filter(aluno=aluno).delete()
    SessaoEstudo.objects.filter(aluno=aluno).delete()
    Disciplina.objects.filter(aluno=aluno).delete()
    Relatorio.objects.filter(aluno=aluno).delete()
    Sugestao.objects.filter(aluno=aluno).delete()
    LogAtividade.objects.filter(aluno=aluno).delete()
    aluno.delete()


def montar_perfil_completo(aluno):
    hoje = timezone.localdate()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_semana_anterior = inicio_semana - timedelta(days=7)
    fim_semana_anterior = inicio_semana - timedelta(days=1)

    sessoes_base = SessaoEstudo.objects.filter(aluno=aluno, data_exclusao__isnull=True)

    total_horas = float(
        sessoes_base.aggregate(t=Sum("tempo_estudo"))["t"] or 0
    )
    horas_semana = float(
        sessoes_base.filter(
            data_sessao__gte=inicio_semana, data_sessao__lte=hoje
        ).aggregate(t=Sum("tempo_estudo"))["t"]
        or 0
    )
    horas_semana_anterior = float(
        sessoes_base.filter(
            data_sessao__gte=inicio_semana_anterior,
            data_sessao__lte=fim_semana_anterior,
        ).aggregate(t=Sum("tempo_estudo"))["t"]
        or 0
    )

    if horas_semana_anterior > 0:
        produtividade = round(
            ((horas_semana - horas_semana_anterior) / horas_semana_anterior) * 100
        )
    elif horas_semana > 0:
        produtividade = 100
    else:
        produtividade = 0

    streak = _dias_sequencia(aluno, hoje)

    tarefas_qs = Tarefa.objects.filter(
        disciplina__aluno=aluno,
        disciplina__data_exclusao__isnull=True,
        data_exclusao__isnull=True,
    )
    cq = tarefas_concluidas_q()
    metas_total = tarefas_qs.count()
    metas_atingidas = tarefas_qs.filter(cq).count()

    ranking = (
        SessaoEstudo.objects.filter(data_exclusao__isnull=True)
        .values("aluno_id")
        .annotate(horas=Sum("tempo_estudo"))
        .order_by("-horas", "aluno_id")
    )
    posicao = 1
    for i, row in enumerate(ranking, start=1):
        if row["aluno_id"] == aluno.id_aluno:
            posicao = i
            break

    meta_semanal_ok = horas_semana >= 25
    sequencia_ok = streak >= 7
    dedicado_ok = total_horas >= 100

    conquistas = [
        {
            "id": "meta_semanal",
            "titulo": "Meta Semanal",
            "descricao": (
                "25h completadas"
                if meta_semanal_ok
                else f"{round(horas_semana, 1)}h / 25h esta semana"
            ),
            "desbloqueada": meta_semanal_ok,
            "cor": "azul",
        },
        {
            "id": "sequencia",
            "titulo": "Sequência",
            "descricao": (
                f"{streak} dias seguidos"
                if streak > 0
                else "Estude hoje para iniciar"
            ),
            "desbloqueada": sequencia_ok,
            "cor": "roxo",
        },
        {
            "id": "dedicado",
            "titulo": "Dedicado",
            "descricao": (
                "100h totais"
                if dedicado_ok
                else f"{round(total_horas, 1)}h / 100h totais"
            ),
            "desbloqueada": dedicado_ok,
            "cor": "verde",
        },
    ]

    desbloqueadas = sum(1 for c in conquistas if c["desbloqueada"])
    sessoes_count = sessoes_base.count()
    disciplinas_count = Disciplina.objects.filter(
        aluno=aluno, data_exclusao__isnull=True
    ).count()
    conquistas_total = min(
        99,
        desbloqueadas
        + int(total_horas // 10)
        + min(sessoes_count, 5)
        + min(disciplinas_count, 3)
        + min(metas_atingidas, 4),
    )

    membro_data = _membro_desde(aluno)

    return {
        "id_aluno": aluno.id_aluno,
        "nome": aluno.nome,
        "email": aluno.email,
        "papel": "Estudante",
        "membro_desde": membro_data.isoformat(),
        "membro_desde_label": _label_mes_ano(membro_data),
        "conquistas_total": conquistas_total,
        "conquistas": conquistas,
        "estatisticas": {
            "produtividade_pct": produtividade,
            "metas_atingidas": metas_atingidas,
            "metas_total": max(metas_total, 1),
            "ranking": posicao,
        },
        "totais": {
            "horas_estudo": round(total_horas, 1),
            "horas_semana": round(horas_semana, 1),
            "dias_sequencia": streak,
        },
    }
