from django.db import models

from apps.alunos.models import Aluno
from apps.sistema_estudos.models import Disciplina


class Caderno(models.Model):
    id_caderno = models.AutoField(primary_key=True)
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        db_column="aluno_id_aluno",
        related_name="cadernos",
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.SET_NULL,
        db_column="disciplina_id_disciplina",
        related_name="cadernos",
        null=True,
        blank=True,
    )
    titulo = models.CharField(max_length=150)
    descricao = models.CharField(max_length=500, blank=True, default="")
    cor = models.CharField(max_length=20, blank=True, default="#6366f1")
    icone = models.CharField(max_length=50, blank=True, default="book")
    ordem = models.IntegerField(default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "caderno"
        verbose_name = "Caderno"
        verbose_name_plural = "Cadernos"
        ordering = ["ordem", "titulo"]

    def __str__(self) -> str:
        return self.titulo


class PaginaCaderno(models.Model):
    id_pagina = models.AutoField(primary_key=True)
    caderno = models.ForeignKey(
        Caderno,
        on_delete=models.PROTECT,
        db_column="caderno_id_caderno",
        related_name="paginas",
    )
    titulo = models.CharField(max_length=200)
    conteudo = models.JSONField(default=dict)
    ordem = models.IntegerField(default=0)
    favorita = models.BooleanField(default=False)
    quantidade_palavras = models.IntegerField(default=0)
    quantidade_caracteres = models.IntegerField(default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "pagina_caderno"
        verbose_name = "Página do caderno"
        verbose_name_plural = "Páginas do caderno"
        ordering = ["ordem", "titulo"]

    def __str__(self) -> str:
        return self.titulo


class ImagemCaderno(models.Model):
    id_imagem = models.AutoField(primary_key=True)
    pagina = models.ForeignKey(
        PaginaCaderno,
        on_delete=models.PROTECT,
        db_column="pagina_id_pagina",
        related_name="imagens",
    )
    arquivo = models.FileField(upload_to="uploads/cadernos/%Y/%m/")
    nome_original = models.CharField(max_length=255, blank=True, default="")
    data_upload = models.DateTimeField(auto_now_add=True)
    data_exclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "imagem_caderno"
        verbose_name = "Imagem do caderno"
        verbose_name_plural = "Imagens do caderno"

    def __str__(self) -> str:
        return self.nome_original or f"Imagem #{self.pk}"
