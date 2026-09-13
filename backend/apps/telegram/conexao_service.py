"""Conexão do aluno ao bot Telegram via código temporário."""

import secrets
import string
from datetime import timedelta

from django.utils import timezone

from apps.alunos.models import Aluno
from apps.telegram.models import CodigoConexaoTelegram, ConfiguracaoTelegram

CODIGO_TTL_MINUTOS = 10
CODIGO_ALFABETO = string.ascii_uppercase + string.digits


def _gerar_codigo_unico() -> str:
    for _ in range(10):
        codigo = "".join(secrets.choice(CODIGO_ALFABETO) for _ in range(6))
        if not CodigoConexaoTelegram.objects.filter(
            codigo=codigo, utilizado=False, data_expiracao__gt=timezone.now()
        ).exists():
            return codigo
    return secrets.token_hex(3).upper()[:6]


def obter_ou_criar_config(aluno: Aluno) -> ConfiguracaoTelegram:
    config, _ = ConfiguracaoTelegram.objects.get_or_create(
        aluno=aluno,
        defaults={
            "telegram_ativo": False,
            "notificar_24h": True,
            "notificar_2h": True,
        },
    )
    if config.data_exclusao is not None:
        config.data_exclusao = None
        config.save(update_fields=["data_exclusao"])
    return config


def gerar_codigo_conexao(aluno: Aluno) -> CodigoConexaoTelegram:
    agora = timezone.now()
    CodigoConexaoTelegram.objects.filter(
        aluno=aluno, utilizado=False, data_expiracao__gt=agora
    ).update(utilizado=True)
    return CodigoConexaoTelegram.objects.create(
        aluno=aluno,
        codigo=_gerar_codigo_unico(),
        data_expiracao=agora + timedelta(minutes=CODIGO_TTL_MINUTOS),
    )


def conectar_por_codigo(
    codigo: str,
    chat_id: int,
    username: str = "",
) -> tuple[bool, str]:
    codigo_limpo = (codigo or "").strip().upper()
    if not codigo_limpo:
        return False, "❌ Código inválido ou expirado. Gere um novo código no StudyHub."

    registro = (
        CodigoConexaoTelegram.objects.filter(
            codigo=codigo_limpo,
            utilizado=False,
            data_expiracao__gt=timezone.now(),
        )
        .select_related("aluno")
        .first()
    )
    if not registro:
        return False, "❌ Código inválido ou expirado. Gere um novo código no StudyHub."

    config = obter_ou_criar_config(registro.aluno)
    config.telegram_chat_id = chat_id
    config.telegram_username = (username or "").strip().lstrip("@")[:100]
    config.telegram_ativo = True
    config.data_conexao = timezone.now()
    config.data_exclusao = None
    config.save()

    registro.utilizado = True
    registro.save(update_fields=["utilizado"])

    return True, (
        "✅ Telegram conectado ao StudyHub com sucesso!\n\n"
        "Agora você poderá receber lembretes das suas tarefas."
    )


def desconectar_telegram(aluno: Aluno) -> None:
    config = ConfiguracaoTelegram.objects.filter(
        aluno=aluno, data_exclusao__isnull=True
    ).first()
    if not config:
        return
    config.telegram_ativo = False
    config.telegram_chat_id = None
    config.telegram_username = ""
    config.save(
        update_fields=[
            "telegram_ativo",
            "telegram_chat_id",
            "telegram_username",
            "data_atualizacao",
        ]
    )


def registrar_log_telegram(aluno, acao: str, descricao: str, **kwargs) -> None:
    from apps.sistema_estudos.models import LogAtividade

    LogAtividade.objects.create(
        aluno=aluno,
        acao=acao,
        tabela_afetada=kwargs.get("tabela_afetada", "configuracao_telegram"),
        id_registro_afetado=kwargs.get("id_registro_afetado"),
        descricao=descricao[:255],
        data_hora=timezone.now(),
    )


def processar_mensagem_bot(texto: str, chat_id: int, username: str = "") -> str | None:
    comando = (texto or "").strip()
    if not comando:
        return None

    if comando.lower().startswith("/start"):
        return (
            "Olá! Eu sou o bot de notificações do StudyHub.\n\n"
            "Para conectar sua conta, entre no StudyHub, acesse Perfil > Telegram "
            "e gere seu código de conexão."
        )

    if comando.lower().startswith("/conectar"):
        partes = comando.split(maxsplit=1)
        if len(partes) < 2:
            return "Envie: /conectar SEU_CODIGO"
        ok, msg = conectar_por_codigo(partes[1], chat_id, username)
        if ok:
            registro = (
                CodigoConexaoTelegram.objects.filter(codigo=partes[1].strip().upper())
                .select_related("aluno")
                .first()
            )
            if registro:
                registrar_log_telegram(
                    registro.aluno,
                    "TELEGRAM_CONECTADO",
                    "Aluno conectou o Telegram ao StudyHub.",
                )
        return msg

    return None
