"""Geração e validação de JWT (aluno ou responsável)."""

from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings

TIPO_ALUNO = "ALUNO"
TIPO_RESPONSAVEL = "RESPONSAVEL"


def criar_token_acesso(
    id_aluno: int | None = None,
    *,
    tipo: str = TIPO_ALUNO,
    id_responsavel: int | None = None,
) -> str:
    """
    Compatível com o fluxo antigo: criar_token_acesso(id_aluno).
    Também aceita tipo=RESPONSAVEL com id_responsavel.
    """
    exp = datetime.now(timezone.utc) + timedelta(
        hours=getattr(settings, "JWT_EXPIRATION_HOURS", 24)
    )
    payload = {
        "tipo": tipo,
        "exp": exp,
        "iat": datetime.now(timezone.utc),
    }
    if tipo == TIPO_RESPONSAVEL:
        if id_responsavel is None:
            raise ValueError("id_responsavel é obrigatório para tipo RESPONSAVEL")
        payload["id_responsavel"] = id_responsavel
    else:
        aluno_id = id_aluno
        if aluno_id is None:
            raise ValueError("id_aluno é obrigatório para tipo ALUNO")
        payload["id_aluno"] = aluno_id
        payload["tipo"] = TIPO_ALUNO

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token if isinstance(token, str) else token.decode("utf-8")


def decodificar_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None
