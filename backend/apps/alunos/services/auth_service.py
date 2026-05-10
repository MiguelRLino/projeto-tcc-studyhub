"""Geração e validação de JWT para sessão do aluno (sem depender do User do Django)."""

from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings


def criar_token_acesso(id_aluno: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(
        hours=getattr(settings, "JWT_EXPIRATION_HOURS", 24)
    )
    payload = {
        "id_aluno": id_aluno,
        "exp": exp,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decodificar_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None
