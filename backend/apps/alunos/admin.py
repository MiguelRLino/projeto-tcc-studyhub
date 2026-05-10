from django.contrib import admin

from apps.alunos.models import Aluno


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("id_aluno", "nome", "email")
    search_fields = ("nome", "email")
    ordering = ("nome",)
