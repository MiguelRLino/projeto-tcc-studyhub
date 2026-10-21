"""Agrega dados acadêmicos somente-leitura para o painel do responsável."""

from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from apps.alunos.models import Aluno
from apps.sistema_estudos.models import (
    Disciplina,
    SessaoEstudo,
    SessaoPlanejada,
    Tarefa,
)
from apps.sistema_estudos.querysets import (
    disciplinas_ativas_com_metricas,
    tarefas_concluidas_q,
)

META_SEMANAL_HORAS = 10.0


def _tarefas_base(aluno: Aluno):
    return Tarefa.objects.filter(
        disciplina__aluno=aluno,
        disciplina__data_exclusao__isnull=True,
        data_exclusao__isnull=True,
    ).select_related("disciplina")


def montar_dashboard(aluno: Aluno) -> dict:
    hoje = timezone.localdate()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    cq = tarefas_concluidas_q()
    tarefas_qs = _tarefas_base(aluno)

    disciplinas_ativas = Disciplina.objects.filter(
        aluno=aluno, data_exclusao__isnull=True
    ).count()

    pendentes = tarefas_qs.exclude(cq).count()
    concluidas = tarefas_qs.filter(cq).count()
    atrasadas = (
        tarefas_qs.exclude(cq)
        .filter(data_entrega__lt=hoje)
        .count()
    )

    sessoes_base = SessaoEstudo.objects.filter(
        aluno=aluno, data_exclusao__isnull=True
    )
    horas_semana = float(
        sessoes_base.filter(
            data_sessao__gte=inicio_semana,
            data_sessao__lte=hoje,
        ).aggregate(total=Sum("tempo_estudo"))["total"]
        or 0
    )
    total_sessoes_semana = sessoes_base.filter(
        data_sessao__gte=inicio_semana,
        data_sessao__lte=hoje,
    ).count()

    dias_ordem = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    horas_por_dia = [0.0] * 7
    for s in sessoes_base.filter(
        data_sessao__gte=inicio_semana,
        data_sessao__lte=hoje,
    ).only("data_sessao", "tempo_estudo"):
        if s.data_sessao:
            horas_por_dia[s.data_sessao.weekday()] += float(s.tempo_estudo or 0)

    proximas = list(
        tarefas_qs.exclude(cq)
        .filter(data_entrega__gte=hoje)
        .order_by("data_entrega", "hora_entrega")[:5]
    )
    proximas_payload = [
        {
            "id_tarefa": t.id_tarefa,
            "descricao": t.descricao,
            "data_entrega": t.data_entrega.isoformat() if t.data_entrega else None,
            "hora_entrega": t.hora_entrega.isoformat() if t.hora_entrega else None,
            "status_tarefa": t.status_tarefa,
            "disciplina": t.disciplina.nome if t.disciplina else None,
        }
        for t in proximas
    ]

    return {
        "aluno": {
            "id_aluno": aluno.id_aluno,
            "nome": aluno.nome,
            "email": aluno.email,
        },
        "resumo": {
            "disciplinas_ativas": disciplinas_ativas,
            "sessoes_semana": total_sessoes_semana,
            "horas_estudadas_semana": round(horas_semana, 2),
            "tarefas_pendentes": pendentes,
            "tarefas_concluidas": concluidas,
            "tarefas_atrasadas": atrasadas,
        },
        "grafico_horas_semana": [
            {"dia": dias_ordem[i], "horas": round(horas_por_dia[i], 2)}
            for i in range(7)
        ],
        "proximas_entregas": proximas_payload,
    }


def _status_concluido(status: str | None) -> bool:
    if not status:
        return False
    s = status.strip().lower()
    return s in {
        "concluida",
        "concluída",
        "concluido",
        "concluído",
        "feito",
        "done",
    }


def listar_tarefas(aluno: Aluno) -> list[dict]:
    hoje = timezone.localdate()
    itens = []
    for t in _tarefas_base(aluno).order_by("data_entrega", "hora_entrega"):
        is_concluida = _status_concluido(t.status_tarefa)
        atrasada = (
            not is_concluida
            and t.data_entrega is not None
            and t.data_entrega < hoje
        )
        itens.append(
            {
                "id_tarefa": t.id_tarefa,
                "descricao": t.descricao,
                "data_entrega": t.data_entrega.isoformat() if t.data_entrega else None,
                "hora_entrega": t.hora_entrega.isoformat() if t.hora_entrega else None,
                "status_tarefa": t.status_tarefa,
                "disciplina": t.disciplina.nome if t.disciplina else None,
                "atrasada": atrasada,
                "concluida": is_concluida,
            }
        )
    return itens


def listar_disciplinas(aluno: Aluno) -> list[dict]:
    return [
        {
            "id_disciplina": d.id_disciplina,
            "nome": d.nome,
            "nivel_dificuldade": d.nivel_dificuldade,
            "horas_estudadas": float(d.horas_estudadas or 0),
            "tarefas_pendentes": int(d.tarefas_pendentes or 0),
        }
        for d in disciplinas_ativas_com_metricas(aluno)
    ]


def listar_sessoes(aluno: Aluno) -> dict:
    realizadas = [
        {
            "id_sessao_estudo": s.id_sessao_estudo,
            "disciplina": s.disciplina.nome if s.disciplina else None,
            "data_sessao": s.data_sessao.isoformat() if s.data_sessao else None,
            "tempo_estudo": float(s.tempo_estudo or 0),
            "nivel_dificuldade": s.nivel_dificuldade,
        }
        for s in SessaoEstudo.objects.filter(
            aluno=aluno, data_exclusao__isnull=True
        )
        .select_related("disciplina")
        .order_by("-data_sessao")[:50]
    ]
    planejadas = [
        {
            "id_sessao_planejada": s.id_sessao_planejada,
            "disciplina": s.disciplina.nome if s.disciplina else None,
            "data_planejada": s.data_planejada.isoformat() if s.data_planejada else None,
            "duracao_prevista_minutos": s.duracao_prevista_minutos,
            "observacao": s.observacao,
        }
        for s in SessaoPlanejada.objects.filter(
            aluno=aluno, data_exclusao__isnull=True
        )
        .select_related("disciplina")
        .order_by("data_planejada")[:50]
    ]
    return {"realizadas": realizadas, "planejadas": planejadas}


def montar_relatorios(aluno: Aluno) -> dict:
    hoje = timezone.localdate()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    cq = tarefas_concluidas_q()
    base_sessoes = SessaoEstudo.objects.filter(
        aluno=aluno, data_exclusao__isnull=True
    )
    total_horas = float(
        base_sessoes.aggregate(total=Sum("tempo_estudo"))["total"] or 0
    )
    disciplinas = list(disciplinas_ativas_com_metricas(aluno))
    qtd = len(disciplinas)
    media = round(total_horas / qtd, 1) if qtd else 0.0

    melhor_nome = "—"
    melhor_horas = 0.0
    distribuicao = []
    for disc in disciplinas:
        horas = float(disc.horas_estudadas or 0)
        if horas > melhor_horas:
            melhor_horas = horas
            melhor_nome = disc.nome or "—"
        if horas > 0:
            distribuicao.append(
                {"disciplina": disc.nome or "Disciplina", "horas": round(horas, 1)}
            )
    distribuicao.sort(key=lambda x: x["horas"], reverse=True)

    horas_semana = float(
        base_sessoes.filter(
            data_sessao__gte=inicio_semana,
            data_sessao__lte=hoje,
        ).aggregate(total=Sum("tempo_estudo"))["total"]
        or 0
    )

    dias_ordem = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    horas_por_dia = [0.0] * 7
    for sessao in base_sessoes.filter(
        data_sessao__gte=inicio_semana,
        data_sessao__lte=hoje,
    ).only("data_sessao", "tempo_estudo"):
        if sessao.data_sessao:
            horas_por_dia[sessao.data_sessao.weekday()] += float(
                sessao.tempo_estudo or 0
            )

    evolucao = []
    for offset in range(3, -1, -1):
        inicio = inicio_semana - timedelta(weeks=offset)
        fim = inicio + timedelta(days=6)
        horas = float(
            base_sessoes.filter(
                data_sessao__gte=inicio,
                data_sessao__lte=fim,
            ).aggregate(total=Sum("tempo_estudo"))["total"]
            or 0
        )
        evolucao.append({"semana": f"Sem {4 - offset}", "horas": round(horas, 1)})

    tarefas_concluidas = _tarefas_base(aluno).filter(cq).count()

    return {
        "total_horas": round(total_horas, 1),
        "media_por_disciplina": media,
        "melhor_disciplina": melhor_nome,
        "melhor_disciplina_horas": round(melhor_horas, 1),
        "horas_estudadas_semana": round(horas_semana, 1),
        "meta_semanal_horas": META_SEMANAL_HORAS,
        "meta_semanal_pct": min(
            100, round(horas_semana / META_SEMANAL_HORAS * 100)
        )
        if META_SEMANAL_HORAS
        else 0,
        "grafico_horas_semana": [
            {"dia": dias_ordem[i], "horas": round(horas_por_dia[i], 1)}
            for i in range(7)
        ],
        "distribuicao_disciplinas": distribuicao,
        "evolucao_semanal": evolucao,
        "tarefas_concluidas": tarefas_concluidas,
    }
