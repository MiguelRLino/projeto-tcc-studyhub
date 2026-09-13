"""Token e e-mail para redefinição de senha."""

from datetime import datetime, timedelta, timezone

import jwt
from urllib.parse import quote

from django.conf import settings
from django.core.mail import send_mail

from apps.alunos.models import Aluno

RESET_EXPIRATION_HOURS = int(getattr(settings, "PASSWORD_RESET_HOURS", "1"))


def criar_token_recuperacao(id_aluno: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=RESET_EXPIRATION_HOURS)
    payload = {
        "id_aluno": id_aluno,
        "purpose": "password_reset",
        "exp": exp,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token if isinstance(token, str) else token.decode("utf-8")


def validar_token_recuperacao(token: str) -> int | None:
    try:
        data = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None
    if data.get("purpose") != "password_reset":
        return None
    return data.get("id_aluno")


def montar_link_redefinicao(token: str) -> str:
    base = getattr(settings, "FRONTEND_URL", "http://localhost:5173").rstrip("/")
    token_codificado = quote(token, safe="")
    return f"{base}/redefinir-senha?token={token_codificado}"


def enviar_email_recuperacao(aluno: Aluno, token: str) -> None:
    link = montar_link_redefinicao(token)
    assunto = "StudyHub — Redefinir sua senha"
    mensagem = (
        f"Olá, {aluno.nome}!\n\n"
        "Recebemos um pedido para redefinir a senha da sua conta no StudyHub.\n"
        f"Acesse o link abaixo (válido por {RESET_EXPIRATION_HOURS} hora(s)):\n\n"
        f"{link}\n\n"
        "Se você não solicitou isso, ignore este e-mail.\n\n"
        "— Equipe StudyHub"
    )
    remetente = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@studyhub.local")
    send_mail(
        assunto,
        mensagem,
        remetente,
        [aluno.email],
        fail_silently=False,
    )
