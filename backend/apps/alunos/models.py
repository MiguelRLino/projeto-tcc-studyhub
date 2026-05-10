"""
Modelo Aluno — tabela `aluno` no banco `sistema_estudos`.

Demais tabelas (disciplina, tarefa, sessao_estudo, relatorio, sugestao, log_atividade)
estão em `apps.sistema_estudos.models`.
"""

from django.db import models


class Aluno(models.Model):
    """Aluno da plataforma. A coluna `senha` armazena apenas hash (PBKDF2 via Django)."""

    id_aluno = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    senha = models.CharField(max_length=255)

    class Meta:
        db_table = "aluno"
        ordering = ["nome"]
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"

    def __str__(self) -> str:
        return f"{self.nome} <{self.email}>"
