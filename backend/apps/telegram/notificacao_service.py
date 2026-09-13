"""Verificação de vencimento e envio de notificações de tarefas."""

import logging
from datetime import datetime, time, timedelta

from django.utils import timezone

from apps.sistema_estudos.models import Tarefa
from apps.sistema_estudos.querysets import tarefas_concluidas_q
from apps.telegram.conexao_service import registrar_log_telegram
from apps.telegram.models import ConfiguracaoTelegram, NotificacaoTelegram
from apps.telegram.services import TelegramService, TelegramServiceError

logger = logging.getLogger(__name__)

HORA_PADRAO_ENTREGA = time(23, 59, 59)
JANELA_24H_MIN = timedelta(hours=23)
JANELA_24H_MAX = timedelta(hours=25)
JANELA_2H_MIN = timedelta(hours=1, minutes=30)
JANELA_2H_MAX = timedelta(hours=2, minutes=30)


def datetime_entrega_tarefa(tarefa: Tarefa) -> datetime | None:
    if not tarefa.data_entrega:
        return None
    hora = getattr(tarefa, "hora_entrega", None) or HORA_PADRAO_ENTREGA
    tz = timezone.get_current_timezone()
    return timezone.make_aware(datetime.combine(tarefa.data_entrega, hora), tz)


def tarefa_pendente_qs():
    return (
        Tarefa.objects.filter(
            data_exclusao__isnull=True,
            data_entrega__isnull=False,
            disciplina__data_exclusao__isnull=True,
            disciplina__aluno__isnull=False,
        )
        .exclude(tarefas_concluidas_q())
        .select_related("disciplina", "disciplina__aluno")
    )


def _formatar_status(status: str) -> str:
    s = (status or "pendente").strip().lower()
    return s.capitalize() if s else "Pendente"


def montar_mensagem_tarefa(tarefa: Tarefa, tipo: str) -> str:
    disciplina = tarefa.disciplina.nome if tarefa.disciplina else "—"
    data_fmt = tarefa.data_entrega.strftime("%d/%m/%Y") if tarefa.data_entrega else "—"
    hora = getattr(tarefa, "hora_entrega", None)
    if hora:
        data_fmt += f" às {hora.strftime('%H:%M')}"

    if tipo == NotificacaoTelegram.TIPO_TAREFA_24H:
        prazo = "vence amanhã"
    else:
        prazo = "vence em breve (cerca de 2 horas)"

    titulo = (tarefa.descricao or "Tarefa").strip()
    return (
        f"🔔 StudyHub\n\n"
        f'Sua tarefa "{titulo}" {prazo}.\n\n'
        f"Disciplina: {disciplina}\n"
        f"Data de entrega: {data_fmt}\n"
        f"Status: {_formatar_status(tarefa.status_tarefa)}\n\n"
        f"Não esqueça de finalizar a atividade."
    )


def _dentro_janela(restante: timedelta, minimo: timedelta, maximo: timedelta) -> bool:
    return minimo <= restante <= maximo


def _ja_notificou(aluno_id: int, tarefa_id: int, tipo: str) -> bool:
    return NotificacaoTelegram.objects.filter(
        aluno_id=aluno_id,
        tarefa_id=tarefa_id,
        tipo=tipo,
        status_envio=NotificacaoTelegram.STATUS_ENVIADO,
    ).exists()


def _enviar_notificacao(config: ConfiguracaoTelegram, tarefa: Tarefa, tipo: str) -> str:
    aluno = config.aluno
    if _ja_notificou(aluno.pk, tarefa.pk, tipo):
        return "ignorado"

    mensagem = montar_mensagem_tarefa(tarefa, tipo)
    try:
        TelegramService.enviar_mensagem(config.telegram_chat_id, mensagem)
        NotificacaoTelegram.objects.create(
            aluno=aluno,
            tarefa=tarefa,
            tipo=tipo,
            status_envio=NotificacaoTelegram.STATUS_ENVIADO,
        )
        registrar_log_telegram(
            aluno,
            "NOTIFICACAO_TELEGRAM_ENVIADA",
            "Notificação de vencimento de tarefa enviada pelo Telegram.",
            tabela_afetada="tarefa",
            id_registro_afetado=tarefa.pk,
        )
        return "enviado"
    except TelegramServiceError as exc:
        NotificacaoTelegram.objects.update_or_create(
            aluno=aluno,
            tarefa=tarefa,
            tipo=tipo,
            defaults={
                "status_envio": NotificacaoTelegram.STATUS_ERRO,
                "erro": str(exc)[:255],
            },
        )
        registrar_log_telegram(
            aluno,
            "ERRO_NOTIFICACAO_TELEGRAM",
            "Falha ao enviar notificação de tarefa pelo Telegram.",
            tabela_afetada="tarefa",
            id_registro_afetado=tarefa.pk,
        )
        logger.error("Erro notificação tarefa %s: %s", tarefa.pk, exc)
        return "erro"


def verificar_e_enviar_notificacoes(agora: datetime | None = None) -> dict:
    agora = agora or timezone.now()
    stats = {"analisadas": 0, "enviadas": 0, "ignoradas": 0, "erros": 0}

    configs = {
        c.aluno_id: c
        for c in ConfiguracaoTelegram.objects.filter(
            data_exclusao__isnull=True,
            telegram_ativo=True,
            telegram_chat_id__isnull=False,
        ).select_related("aluno")
    }

    for tarefa in tarefa_pendente_qs():
        stats["analisadas"] += 1
        aluno_id = tarefa.disciplina.aluno_id
        config = configs.get(aluno_id)
        if not config or not config.telegram_ativo:
            stats["ignoradas"] += 1
            continue

        entrega = datetime_entrega_tarefa(tarefa)
        if not entrega or entrega <= agora:
            stats["ignoradas"] += 1
            continue

        restante = entrega - agora
        tipos: list[str] = []
        if config.notificar_24h and _dentro_janela(restante, JANELA_24H_MIN, JANELA_24H_MAX):
            tipos.append(NotificacaoTelegram.TIPO_TAREFA_24H)
        if config.notificar_2h and _dentro_janela(restante, JANELA_2H_MIN, JANELA_2H_MAX):
            tipos.append(NotificacaoTelegram.TIPO_TAREFA_2H)

        if not tipos:
            stats["ignoradas"] += 1
            continue

        for tipo in tipos:
            resultado = _enviar_notificacao(config, tarefa, tipo)
            if resultado == "enviado":
                stats["enviadas"] += 1
            elif resultado == "ignorado":
                stats["ignoradas"] += 1
            else:
                stats["erros"] += 1

    return stats


def enviar_mensagem_teste(aluno) -> None:
    config = ConfiguracaoTelegram.objects.filter(
        aluno=aluno,
        data_exclusao__isnull=True,
        telegram_ativo=True,
        telegram_chat_id__isnull=False,
    ).first()
    if not config:
        raise TelegramServiceError("Telegram não conectado para este aluno.")
    TelegramService.enviar_mensagem(
        config.telegram_chat_id,
        "✅ Teste do StudyHub\n\n"
        "Se você recebeu esta mensagem, sua integração com Telegram "
        "está funcionando corretamente.",
    )
