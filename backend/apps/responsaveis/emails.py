from django.conf import settings
from django.core.mail import send_mail

from apps.alunos.models import Aluno
from apps.responsaveis.models import ConviteResponsavel


def montar_link_convite(token: str) -> str:
    base = getattr(settings, "FRONTEND_URL", "http://localhost:5173").rstrip("/")
    return f"{base}/convite/responsavel/{token}"


def enviar_email_convite(
    convite: ConviteResponsavel,
    token: str,
    aluno: Aluno,
) -> None:
    link = montar_link_convite(token)
    horas = int(getattr(settings, "RESPONSAVEL_CONVITE_HORAS", 48))
    assunto = "Convite para acompanhar estudos no StudyHub"
    mensagem = (
        f"Olá, {convite.nome_convidado}!\n\n"
        f"Você recebeu um convite para acompanhar o progresso de estudos de "
        f"{aluno.nome} no StudyHub.\n\n"
        "Para aceitar e criar seu acesso, clique no link abaixo:\n\n"
        f"{link}\n\n"
        f"Este convite é válido por {horas} hora(s).\n\n"
        "Se você não reconhece este convite, ignore este e-mail.\n\n"
        "— Equipe StudyHub"
    )
    remetente = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@studyhub.local")
    send_mail(
        assunto,
        mensagem,
        remetente,
        [convite.email_convidado],
        fail_silently=False,
    )
