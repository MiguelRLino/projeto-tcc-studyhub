from django.contrib import admin

from apps.assistente_ia.models import ConversaIA


@admin.register(ConversaIA)
class ConversaIAAdmin(admin.ModelAdmin):
    list_display = ("id_conversa", "aluno", "data_criacao", "data_exclusao")
    list_filter = ("data_exclusao",)
    search_fields = ("pergunta", "aluno__nome", "aluno__email")
    readonly_fields = ("data_criacao",)
