from django.contrib import admin

from apps.sistema_estudos.models import (
    Disciplina,
    LogAtividade,
    Relatorio,
    SessaoEstudo,
    Sugestao,
    Tarefa,
)


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ("id_disciplina", "nome", "aluno", "nivel_dificuldade", "data_exclusao")
    list_filter = ("data_exclusao",)
    search_fields = ("nome",)


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ("id_tarefa", "descricao", "disciplina", "data_entrega", "status_tarefa")
    search_fields = ("descricao",)


@admin.register(SessaoEstudo)
class SessaoEstudoAdmin(admin.ModelAdmin):
    list_display = (
        "id_sessao_estudo",
        "aluno",
        "disciplina",
        "tempo_estudo",
        "data_sessao",
        "nivel_dificuldade",
    )


@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ("id_relatorio", "aluno", "periodo", "total_horas", "data_exclusao")


@admin.register(Sugestao)
class SugestaoAdmin(admin.ModelAdmin):
    list_display = ("id_sugestao", "aluno", "descricao", "data_exclusao")


@admin.register(LogAtividade)
class LogAtividadeAdmin(admin.ModelAdmin):
    list_display = (
        "id_log_atividade",
        "aluno",
        "acao",
        "tabela_afetada",
        "id_registro_afetado",
        "data_hora",
    )
