"""Convites, vínculos e logs do módulo responsáveis."""

from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone

from apps.alunos.models import Aluno
from apps.alunos.services.auth_service import TIPO_RESPONSAVEL, criar_token_acesso
from apps.responsaveis.emails import enviar_email_convite
from apps.responsaveis.models import (
    ConviteResponsavel,
    Parentesco,
    Responsavel,
    ResponsavelAluno,
    StatusConvite,
    StatusVinculo,
)
from apps.sistema_estudos.models import LogAtividade

CONVITE_HORAS = int(getattr(settings, "RESPONSAVEL_CONVITE_HORAS", 48))


class ConviteErro(Exception):
    def __init__(self, mensagem: str, status_code: int = 400):
        self.mensagem = mensagem
        self.status_code = status_code
        super().__init__(mensagem)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def gerar_token_convite() -> str:
    return secrets.token_urlsafe(32)


def registrar_log_responsavel(
    aluno: Aluno,
    acao: str,
    *,
    tabela: str = "responsavel_aluno",
    id_registro: int | None = None,
    descricao: str = "",
) -> None:
    LogAtividade.objects.create(
        aluno=aluno,
        acao=acao,
        tabela_afetada=tabela,
        id_registro_afetado=id_registro,
        descricao=(descricao or "")[:255],
        data_hora=timezone.now(),
    )


def email_ja_e_aluno(email: str) -> bool:
    return Aluno.objects.filter(email__iexact=email.strip()).exists()


def email_ja_e_responsavel(email: str) -> bool:
    return Responsavel.objects.filter(email__iexact=email.strip()).exists()


def _vinculo_ativo_existente(aluno: Aluno, email: str) -> bool:
    return ResponsavelAluno.objects.filter(
        aluno=aluno,
        responsavel__email__iexact=email.strip(),
        status=StatusVinculo.ATIVO,
        data_exclusao__isnull=True,
    ).exists()


def _convite_pendente_existente(aluno: Aluno, email: str) -> ConviteResponsavel | None:
    agora = timezone.now()
    return (
        ConviteResponsavel.objects.filter(
            aluno=aluno,
            email_convidado__iexact=email.strip(),
            status=StatusConvite.PENDENTE,
            data_exclusao__isnull=True,
            data_expiracao__gt=agora,
        )
        .order_by("-data_criacao")
        .first()
    )


def convidar_responsavel(
    aluno: Aluno,
    *,
    nome: str,
    email: str,
    parentesco: str,
) -> tuple[ConviteResponsavel, str | None]:
    email_norm = email.strip().lower()
    nome = nome.strip()

    if parentesco not in Parentesco.values:
        raise ConviteErro("Parentesco inválido.")

    if email_ja_e_aluno(email_norm):
        raise ConviteErro(
            "Este e-mail já pertence a um aluno. Use outro e-mail para o responsável."
        )

    if _vinculo_ativo_existente(aluno, email_norm):
        raise ConviteErro("Este responsável já está vinculado à sua conta.")

    with transaction.atomic():
        # Invalida convites pendentes anteriores para o mesmo e-mail
        ConviteResponsavel.objects.filter(
            aluno=aluno,
            email_convidado__iexact=email_norm,
            status=StatusConvite.PENDENTE,
            data_exclusao__isnull=True,
        ).update(status=StatusConvite.CANCELADO)

        token = gerar_token_convite()
        convite = ConviteResponsavel.objects.create(
            aluno=aluno,
            nome_convidado=nome,
            email_convidado=email_norm,
            parentesco=parentesco,
            token_hash=_hash_token(token),
            data_expiracao=timezone.now() + timedelta(hours=CONVITE_HORAS),
            status=StatusConvite.PENDENTE,
        )

    try:
        enviar_email_convite(convite, token, aluno)
    except Exception as exc:
        # Persistido fora do atomic para sobreviver ao erro de envio
        ConviteResponsavel.objects.filter(pk=convite.pk).update(
            status=StatusConvite.FALHA_ENVIO
        )
        raise ConviteErro(
            "Não foi possível enviar o e-mail do convite. Tente novamente.",
            status_code=502,
        ) from exc

    registrar_log_responsavel(
        aluno,
        "CONVITE_RESPONSAVEL_ENVIADO",
        tabela="convite_responsavel",
        id_registro=convite.id_convite,
        descricao=f"Convite enviado para {email_norm}",
    )
    link_dev = None
    if settings.DEBUG:
        from apps.responsaveis.emails import montar_link_convite

        link_dev = montar_link_convite(token)
    return convite, link_dev


def reenviar_convite(aluno: Aluno, convite_id: int) -> tuple[ConviteResponsavel, str | None]:
    try:
        antigo = ConviteResponsavel.objects.get(
            pk=convite_id,
            aluno=aluno,
            data_exclusao__isnull=True,
        )
    except ConviteResponsavel.DoesNotExist as exc:
        raise ConviteErro("Convite não encontrado.", status_code=404) from exc

    if antigo.status == StatusConvite.ACEITO:
        raise ConviteErro("Este convite já foi aceito.")

    if _vinculo_ativo_existente(aluno, antigo.email_convidado):
        raise ConviteErro("Este responsável já está vinculado.")

    with transaction.atomic():
        antigo.status = StatusConvite.CANCELADO
        antigo.save(update_fields=["status"])

        token = gerar_token_convite()
        novo = ConviteResponsavel.objects.create(
            aluno=aluno,
            nome_convidado=antigo.nome_convidado,
            email_convidado=antigo.email_convidado,
            parentesco=antigo.parentesco,
            token_hash=_hash_token(token),
            data_expiracao=timezone.now() + timedelta(hours=CONVITE_HORAS),
            status=StatusConvite.PENDENTE,
        )

    try:
        enviar_email_convite(novo, token, aluno)
    except Exception as exc:
        ConviteResponsavel.objects.filter(pk=novo.pk).update(
            status=StatusConvite.FALHA_ENVIO
        )
        raise ConviteErro(
            "Não foi possível reenviar o e-mail. Tente novamente.",
            status_code=502,
        ) from exc

    registrar_log_responsavel(
        aluno,
        "CONVITE_RESPONSAVEL_REENVIADO",
        tabela="convite_responsavel",
        id_registro=novo.id_convite,
        descricao=f"Convite reenviado para {novo.email_convidado}",
    )
    link_dev = None
    if settings.DEBUG:
        from apps.responsaveis.emails import montar_link_convite

        link_dev = montar_link_convite(token)
    return novo, link_dev


@transaction.atomic
def cancelar_convite(aluno: Aluno, convite_id: int) -> None:
    try:
        convite = ConviteResponsavel.objects.get(
            pk=convite_id,
            aluno=aluno,
            data_exclusao__isnull=True,
        )
    except ConviteResponsavel.DoesNotExist as exc:
        raise ConviteErro("Convite não encontrado.", status_code=404) from exc

    if convite.status == StatusConvite.ACEITO:
        raise ConviteErro("Não é possível cancelar um convite já aceito.")

    convite.status = StatusConvite.CANCELADO
    convite.data_exclusao = timezone.now()
    convite.save(update_fields=["status", "data_exclusao"])
    registrar_log_responsavel(
        aluno,
        "CONVITE_RESPONSAVEL_CANCELADO",
        tabela="convite_responsavel",
        id_registro=convite.id_convite,
        descricao=f"Convite cancelado: {convite.email_convidado}",
    )


@transaction.atomic
def remover_vinculo(aluno: Aluno, vinculo_id: int) -> None:
    try:
        vinculo = ResponsavelAluno.objects.get(
            pk=vinculo_id,
            aluno=aluno,
            data_exclusao__isnull=True,
        )
    except ResponsavelAluno.DoesNotExist as exc:
        raise ConviteErro("Vínculo não encontrado.", status_code=404) from exc

    vinculo.status = StatusVinculo.CANCELADO
    vinculo.data_exclusao = timezone.now()
    vinculo.save(update_fields=["status", "data_exclusao", "data_atualizacao"])
    registrar_log_responsavel(
        aluno,
        "RESPONSAVEL_REMOVIDO",
        tabela="responsavel_aluno",
        id_registro=vinculo.id_vinculo,
        descricao="Acesso do responsável removido pelo aluno",
    )


def obter_convite_por_token(token: str) -> ConviteResponsavel | None:
    if not token:
        return None
    token_h = _hash_token(token.strip())
    convite = (
        ConviteResponsavel.objects.select_related("aluno")
        .filter(token_hash=token_h, data_exclusao__isnull=True)
        .first()
    )
    if not convite:
        return None
    if convite.status == StatusConvite.PENDENTE and convite.data_expiracao <= timezone.now():
        convite.status = StatusConvite.EXPIRADO
        convite.save(update_fields=["status"])
    return convite


def validar_convite_publico(token: str) -> dict:
    convite = obter_convite_por_token(token)
    if not convite:
        raise ConviteErro("Convite inválido ou inexistente.", status_code=404)
    if convite.status == StatusConvite.ACEITO:
        raise ConviteErro("Este convite já foi utilizado.")
    if convite.status == StatusConvite.CANCELADO:
        raise ConviteErro("Este convite foi cancelado.")
    if convite.status == StatusConvite.EXPIRADO or convite.data_expiracao <= timezone.now():
        if convite.status != StatusConvite.EXPIRADO:
            convite.status = StatusConvite.EXPIRADO
            convite.save(update_fields=["status"])
        raise ConviteErro("Este convite expirou.")
    if convite.status != StatusConvite.PENDENTE:
        raise ConviteErro("Este convite não está disponível.")

    conta_existe = email_ja_e_responsavel(convite.email_convidado)
    return {
        "valido": True,
        "nome_convidado": convite.nome_convidado,
        "email_convidado": convite.email_convidado,
        "parentesco": convite.parentesco,
        "nome_aluno": convite.aluno.nome,
        "conta_existe": conta_existe,
        "expira_em": convite.data_expiracao.isoformat(),
    }


@transaction.atomic
def aceitar_convite(
    token: str,
    *,
    senha: str | None = None,
    senha_confirmacao: str | None = None,
    responsavel_autenticado: Responsavel | None = None,
) -> dict:
    convite = obter_convite_por_token(token)
    if not convite:
        raise ConviteErro("Convite inválido ou inexistente.", status_code=404)
    if convite.status == StatusConvite.ACEITO:
        raise ConviteErro("Este convite já foi utilizado.")
    if convite.status != StatusConvite.PENDENTE or convite.data_expiracao <= timezone.now():
        raise ConviteErro("Este convite expirou ou não está disponível.")

    email = convite.email_convidado

    if responsavel_autenticado is not None:
        if responsavel_autenticado.email.lower() != email.lower():
            raise ConviteErro(
                "O e-mail autenticado não corresponde ao convite.",
                status_code=403,
            )
        responsavel = responsavel_autenticado
    else:
        existente = Responsavel.objects.filter(email__iexact=email).first()
        if existente:
            raise ConviteErro(
                "Já existe uma conta para este e-mail. Faça login e aceite o convite."
            )
        if not senha or not senha_confirmacao:
            raise ConviteErro("Informe a senha e a confirmação.")
        if senha != senha_confirmacao:
            raise ConviteErro("As senhas não coincidem.")
        if len(senha) < 8:
            raise ConviteErro("A senha deve ter pelo menos 8 caracteres.")

        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError

        try:
            validate_password(senha)
        except ValidationError as exc:
            raise ConviteErro(" ".join(exc.messages)) from exc

        responsavel = Responsavel.objects.create(
            nome=convite.nome_convidado,
            email=email,
            senha=make_password(senha),
        )

    if _vinculo_ativo_existente(convite.aluno, email):
        raise ConviteErro("Vínculo já existe para este aluno.")

    vinculo = ResponsavelAluno.objects.create(
        aluno=convite.aluno,
        responsavel=responsavel,
        parentesco=convite.parentesco,
        status=StatusVinculo.ATIVO,
        data_aceitacao=timezone.now(),
    )

    convite.status = StatusConvite.ACEITO
    convite.data_aceitacao = timezone.now()
    # Invalida o token (hash aleatório novo impossível de reutilizar)
    convite.token_hash = _hash_token(secrets.token_urlsafe(32))
    convite.save(update_fields=["status", "data_aceitacao", "token_hash"])

    registrar_log_responsavel(
        convite.aluno,
        "CONVITE_RESPONSAVEL_ACEITO",
        tabela="responsavel_aluno",
        id_registro=vinculo.id_vinculo,
        descricao=f"Convite aceito por {email}",
    )

    access = criar_token_acesso(
        tipo=TIPO_RESPONSAVEL,
        id_responsavel=responsavel.id_responsavel,
    )
    return {
        "mensagem": "Convite aceito com sucesso.",
        "access": access,
        "tipo": TIPO_RESPONSAVEL,
        "usuario": {
            "id_responsavel": responsavel.id_responsavel,
            "nome": responsavel.nome,
            "email": responsavel.email,
        },
        "vinculo_id": vinculo.id_vinculo,
        "aluno_id": convite.aluno_id,
    }


def listar_meus_responsaveis(aluno: Aluno) -> list[dict]:
    itens: list[dict] = []

    vinculos = (
        ResponsavelAluno.objects.filter(
            aluno=aluno,
            status=StatusVinculo.ATIVO,
            data_exclusao__isnull=True,
        )
        .select_related("responsavel")
        .order_by("responsavel__nome")
    )
    for v in vinculos:
        itens.append(
            {
                "tipo": "vinculo",
                "id": v.id_vinculo,
                "nome": v.responsavel.nome,
                "email": v.responsavel.email,
                "parentesco": v.parentesco,
                "status": "ATIVO",
                "data_aceitacao": v.data_aceitacao,
            }
        )

    agora = timezone.now()
    convites = ConviteResponsavel.objects.filter(
        aluno=aluno,
        status__in=[StatusConvite.PENDENTE, StatusConvite.FALHA_ENVIO],
        data_exclusao__isnull=True,
    ).order_by("-data_criacao")
    for c in convites:
        status = c.status
        if status == StatusConvite.PENDENTE and c.data_expiracao <= agora:
            c.status = StatusConvite.EXPIRADO
            c.save(update_fields=["status"])
            continue
        itens.append(
            {
                "tipo": "convite",
                "id": c.id_convite,
                "nome": c.nome_convidado,
                "email": c.email_convidado,
                "parentesco": c.parentesco,
                "status": "PENDENTE" if status == StatusConvite.PENDENTE else status,
                "data_criacao": c.data_criacao,
                "data_expiracao": c.data_expiracao,
            }
        )
    return itens
