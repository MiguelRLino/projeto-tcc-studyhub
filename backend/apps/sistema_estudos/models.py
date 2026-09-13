"""
Modelos espelhando o schema MySQL `sistema_estudos` (tabelas criadas via SQL ou migrate).

Use `python manage.py migrate` para criar via Django; se as tabelas já existirem pelo script SQL,
use `python manage.py migrate --fake-initial` na primeira vez para alinhar o histórico.
"""

from django.db import models

from apps.alunos.models import Aluno


class Disciplina(models.Model):
    id_disciplina = models.AutoField(primary_key=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="disciplinas",
        null=True,
        blank=True,
    )
    nome = models.CharField(max_length=100, null=True, blank=True)
    nivel_dificuldade = models.IntegerField(null=True, blank=True)
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "disciplina"
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"

    def __str__(self) -> str:
        return self.nome or f"Disciplina #{self.pk}"


class Tarefa(models.Model):
    id_tarefa = models.AutoField(primary_key=True)
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.PROTECT,
        db_column="disciplina_id_disciplina",
        related_name="tarefas",
        null=True,
        blank=True,
    )
    descricao = models.CharField(max_length=255, null=True, blank=True)
    data_entrega = models.DateField(null=True, blank=True)
    hora_entrega = models.TimeField(null=True, blank=True)
    status_tarefa = models.CharField(max_length=20, null=True, blank=True)
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tarefa"
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"

    def __str__(self) -> str:
        return (self.descricao or "")[:50] or f"Tarefa #{self.pk}"


class SessaoEstudo(models.Model):
    id_sessao_estudo = models.AutoField(primary_key=True)
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.PROTECT,
        db_column="disciplina_id_disciplina",
        related_name="sessoes_estudo",
        null=True,
        blank=True,
    )
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="sessoes_estudo",
        null=True,
        blank=True,
    )
    tempo_estudo = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    data_sessao = models.DateField(null=True, blank=True)
    nivel_dificuldade = models.IntegerField(null=True, blank=True)
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sessao_estudo"
        verbose_name = "Sessão de estudo"
        verbose_name_plural = "Sessões de estudo"

    def __str__(self) -> str:
        return f"Sessão #{self.pk}"


class SessaoPlanejada(models.Model):
    id_sessao_planejada = models.AutoField(primary_key=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="sessoes_planejadas",
        null=True,
        blank=True,
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.PROTECT,
        db_column="disciplina_id_disciplina",
        related_name="sessoes_planejadas",
        null=True,
        blank=True,
    )
    data_planejada = models.DateField(null=True, blank=True)
    duracao_prevista_minutos = models.IntegerField(null=True, blank=True)
    observacao = models.CharField(max_length=255, null=True, blank=True)
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sessao_planejada"
        verbose_name = "Sessão planejada"
        verbose_name_plural = "Sessões planejadas"

    def __str__(self) -> str:
        return f"Sessão planejada #{self.pk}"


class Relatorio(models.Model):
    id_relatorio = models.AutoField(primary_key=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="relatorios",
        null=True,
        blank=True,
    )
    periodo = models.CharField(max_length=50, null=True, blank=True)
    total_horas = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "relatorio"
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"

    def __str__(self) -> str:
        return self.periodo or f"Relatório #{self.pk}"


class Sugestao(models.Model):
    id_sugestao = models.AutoField(primary_key=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="sugestoes",
        null=True,
        blank=True,
    )
    descricao = models.CharField(max_length=255, null=True, blank=True)
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sugestao"
        verbose_name = "Sugestão"
        verbose_name_plural = "Sugestões"

    def __str__(self) -> str:
        return (self.descricao or "")[:50] or f"Sugestão #{self.pk}"


class LogAtividade(models.Model):
    id_log_atividade = models.AutoField(primary_key=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="logs_atividade",
        null=True,
        blank=True,
    )
    acao = models.CharField(max_length=150, null=True, blank=True)
    tabela_afetada = models.CharField(max_length=150, null=True, blank=True)
    id_registro_afetado = models.IntegerField(null=True, blank=True)
    descricao = models.CharField(max_length=255, null=True, blank=True)
    data_hora = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "log_atividade"
        verbose_name = "Log de atividade"
        verbose_name_plural = "Logs de atividade"

    def __str__(self) -> str:
        return self.acao or f"Log #{self.pk}"
