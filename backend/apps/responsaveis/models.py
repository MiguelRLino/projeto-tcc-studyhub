from django.db import models

from apps.alunos.models import Aluno


class Parentesco(models.TextChoices):
    PAI = "PAI", "Pai"
    MAE = "MAE", "Mãe"
    OUTRO = "OUTRO", "Outro responsável"


class StatusConvite(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    ACEITO = "ACEITO", "Aceito"
    CANCELADO = "CANCELADO", "Cancelado"
    EXPIRADO = "EXPIRADO", "Expirado"
    FALHA_ENVIO = "FALHA_ENVIO", "Falha no envio"


class StatusVinculo(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    ATIVO = "ATIVO", "Ativo"
    CANCELADO = "CANCELADO", "Cancelado"


class Responsavel(models.Model):
    """Conta própria do responsável (login separado do aluno)."""

    id_responsavel = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    senha = models.CharField(max_length=255)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "responsavel"
        ordering = ["nome"]
        verbose_name = "Responsável"
        verbose_name_plural = "Responsáveis"

    def __str__(self) -> str:
        return f"{self.nome} <{self.email}>"


class ConviteResponsavel(models.Model):
    id_convite = models.AutoField(primary_key=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="convites_responsavel",
    )
    nome_convidado = models.CharField(max_length=100)
    email_convidado = models.EmailField(max_length=150)
    parentesco = models.CharField(max_length=20, choices=Parentesco.choices)
    token_hash = models.CharField(max_length=64, db_index=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField()
    data_aceitacao = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusConvite.choices,
        default=StatusConvite.PENDENTE,
    )
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "convite_responsavel"
        ordering = ["-data_criacao"]
        verbose_name = "Convite responsável"
        verbose_name_plural = "Convites responsável"
        indexes = [
            models.Index(fields=["email_convidado", "status"]),
        ]

    def __str__(self) -> str:
        return f"Convite {self.email_convidado} ({self.status})"


class ResponsavelAluno(models.Model):
    id_vinculo = models.AutoField(primary_key=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="vinculos_responsavel",
    )
    responsavel = models.ForeignKey(
        Responsavel,
        on_delete=models.PROTECT,
        db_column="responsavel_id_responsavel",
        related_name="vinculos_aluno",
    )
    parentesco = models.CharField(max_length=20, choices=Parentesco.choices)
    status = models.CharField(
        max_length=20,
        choices=StatusVinculo.choices,
        default=StatusVinculo.PENDENTE,
    )
    data_convite = models.DateTimeField(auto_now_add=True)
    data_aceitacao = models.DateTimeField(null=True, blank=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "responsavel_aluno"
        ordering = ["-data_aceitacao", "-data_convite"]
        verbose_name = "Vínculo responsável-aluno"
        verbose_name_plural = "Vínculos responsável-aluno"
        constraints = [
            models.UniqueConstraint(
                fields=["aluno", "responsavel"],
                condition=models.Q(
                    status=StatusVinculo.ATIVO,
                    data_exclusao__isnull=True,
                ),
                name="uniq_vinculo_ativo_aluno_responsavel",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.responsavel_id} ↔ {self.aluno_id} ({self.status})"
