"""Serviços do Assistente IA — Gemini, limite de uso e logs."""

import logging

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from apps.assistente_ia.models import ConversaIA
from apps.sistema_estudos.models import LogAtividade

logger = logging.getLogger(__name__)

INSTRUCAO_BASE = (
    "Você é o Assistente de Estudos do StudyHub. Sua função é ajudar estudantes "
    "a entender conteúdos, organizar seus estudos e revisar matérias. "
    "Responda sempre em português do Brasil, de forma simples, didática e objetiva. "
    "Não invente informações. Caso não tenha certeza, informe isso claramente."
)

PERGUNTA_MAX_CARACTERES = 2000
LIMITE_PERGUNTAS_POR_HORA = 10
CACHE_LIMITE_PREFIX = "assistente_ia_limite"
CACHE_LIMITE_TTL = 3600


class GeminiConfigError(Exception):
    """Configuração da Gemini ausente ou inválida."""


class GeminiIndisponivelError(Exception):
    """Falha ao comunicar com a Gemini."""


class LimiteUsoAtingidoError(Exception):
    """Aluno atingiu o limite de perguntas por hora."""


def validar_pergunta(pergunta: str) -> str:
    texto = (pergunta or "").strip()
    if not texto:
        raise ValueError("Informe sua pergunta.")
    if len(texto) > PERGUNTA_MAX_CARACTERES:
        raise ValueError(
            f"A pergunta deve ter no máximo {PERGUNTA_MAX_CARACTERES} caracteres."
        )
    return texto


def _chave_limite(aluno_id: int) -> str:
    return f"{CACHE_LIMITE_PREFIX}:{aluno_id}"


def obter_uso_atual(aluno_id: int) -> int:
    return int(cache.get(_chave_limite(aluno_id), 0))


def verificar_limite_uso(aluno_id: int) -> None:
    if obter_uso_atual(aluno_id) >= LIMITE_PERGUNTAS_POR_HORA:
        raise LimiteUsoAtingidoError(
            "Você atingiu o limite de perguntas. Tente novamente mais tarde."
        )


def registrar_uso(aluno_id: int) -> None:
    chave = _chave_limite(aluno_id)
    atual = cache.get(chave)
    if atual is None:
        cache.set(chave, 1, timeout=CACHE_LIMITE_TTL)
    else:
        try:
            cache.incr(chave)
        except ValueError:
            cache.set(chave, 1, timeout=CACHE_LIMITE_TTL)


def gerar_resposta_gemini(
    pergunta: str,
    *,
    instrucao: str | None = None,
    contexto: str | None = None,
) -> str:
    """
    Envia conteúdo à Gemini e retorna o texto da resposta.
    Reutilizável por outros módulos (ex.: Caderno Digital).
    """
    pergunta = validar_pergunta(pergunta)

    api_key = getattr(settings, "GEMINI_API_KEY", "").strip()
    model = getattr(settings, "GEMINI_MODEL", "").strip()
    if not api_key:
        logger.error("GEMINI_API_KEY não configurada.")
        raise GeminiConfigError("Serviço de IA não configurado.")
    if not model:
        logger.error("GEMINI_MODEL não configurado.")
        raise GeminiConfigError("Serviço de IA não configurado.")

    partes = []
    if contexto and str(contexto).strip():
        partes.append(f"Contexto adicional:\n{str(contexto).strip()}\n\n")
    partes.append(f"Pergunta do aluno:\n{pergunta}")
    conteudo_usuario = "".join(partes)
    system_instruction = instrucao or INSTRUCAO_BASE

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=conteudo_usuario,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
            ),
        )
        texto = (getattr(response, "text", None) or "").strip()
        if not texto:
            raise GeminiIndisponivelError("Resposta vazia da IA.")
        return texto
    except (GeminiConfigError, GeminiIndisponivelError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Erro ao chamar Gemini: %s", type(exc).__name__)
        raise GeminiIndisponivelError("Não foi possível obter resposta da IA.") from exc


def registrar_log_consulta(aluno, conversa_id: int) -> None:
    LogAtividade.objects.create(
        aluno=aluno,
        acao="CONSULTA_IA",
        tabela_afetada="conversa_ia",
        id_registro_afetado=conversa_id,
        descricao="Aluno realizou uma consulta ao Assistente IA.",
        data_hora=timezone.now(),
    )


def salvar_conversa(aluno, pergunta: str, resposta: str) -> ConversaIA:
    return ConversaIA.objects.create(
        aluno=aluno,
        pergunta=pergunta,
        resposta=resposta,
    )


def processar_pergunta(aluno, pergunta: str) -> ConversaIA:
    """Fluxo completo: validação, limite, Gemini, persistência e log."""
    texto = validar_pergunta(pergunta)
    verificar_limite_uso(aluno.pk)
    resposta = gerar_resposta_gemini(texto)
    conversa = salvar_conversa(aluno, texto, resposta)
    registrar_uso(aluno.pk)
    registrar_log_consulta(aluno, conversa.pk)
    return conversa
