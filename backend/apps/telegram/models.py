from django.db import models

from apps.alunos.models import Aluno
from apps.sistema_estudos.models import Tarefa


class ConfiguracaoTelegram(models.Model):
    id_configuracao = models.AutoField(primary_key=True)
    aluno = models.OneToOneField(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="configuracao_telegram",
    )
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)
    telegram_username = models.CharField(max_length=100, blank=True, default="")
    telegram_ativo = models.BooleanField(default=False)
    notificar_24h = models.BooleanField(default=True)
    notificar_2h = models.BooleanField(default=True)
    data_conexao = models.DateTimeField(null=True, blank=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "configuracao_telegram"
        verbose_name = "Configuração Telegram"
        verbose_name_plural = "Configurações Telegram"

    def __str__(self) -> str:
        return f"Telegram — {self.aluno_id}"


class CodigoConexaoTelegram(models.Model):
    id_codigo = models.AutoField(primary_key=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="codigos_telegram",
    )
    codigo = models.CharField(max_length=10, db_index=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField()
    utilizado = models.BooleanField(default=False)

    class Meta:
        db_table = "codigo_conexao_telegram"
        verbose_name = "Código conexão Telegram"
        verbose_name_plural = "Códigos conexão Telegram"
        ordering = ["-data_criacao"]


class NotificacaoTelegram(models.Model):
    TIPO_TAREFA_24H = "TAREFA_24H"
    TIPO_TAREFA_2H = "TAREFA_2H"
    TIPOS = (
        (TIPO_TAREFA_24H, "Tarefa 24h"),
        (TIPO_TAREFA_2H, "Tarefa 2h"),
    )

    STATUS_ENVIADO = "enviado"
    STATUS_ERRO = "erro"

    id_notificacao = models.AutoField(primary_key=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="notificacoes_telegram",
    )
    tarefa = models.ForeignKey(
        Tarefa,
        on_delete=models.PROTECT,
        db_column="tarefa_id_tarefa",
        related_name="notificacoes_telegram",
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)
    status_envio = models.CharField(max_length=20, default=STATUS_ENVIADO)
    data_envio = models.DateTimeField(auto_now_add=True)
    erro = models.CharField(max_length=255, blank=True, default="")
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notificacao_telegram"
        verbose_name = "Notificação Telegram"
        verbose_name_plural = "Notificações Telegram"
        constraints = [
            models.UniqueConstraint(
                fields=["aluno", "tarefa", "tipo"],
                name="uniq_notificacao_telegram_tarefa_tipo",
            )
        ]

    def __str__(self) -> str:
        return f"{self.tipo} — tarefa {self.tarefa_id}"
