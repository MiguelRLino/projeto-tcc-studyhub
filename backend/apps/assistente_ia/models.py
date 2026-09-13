from django.db import models

from apps.alunos.models import Aluno


class ConversaIA(models.Model):
    id_conversa = models.AutoField(primary_key=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="conversas_ia",
    )
    pergunta = models.TextField()
    resposta = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "conversa_ia"
        verbose_name = "Conversa com IA"
        verbose_name_plural = "Conversas com IA"
        ordering = ["-data_criacao"]

    def __str__(self) -> str:
        return f"Conversa #{self.pk} — {self.aluno_id}"
