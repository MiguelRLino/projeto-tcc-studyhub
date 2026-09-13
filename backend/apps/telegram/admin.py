from django.contrib import admin

from apps.telegram.models import (
    CodigoConexaoTelegram,
    ConfiguracaoTelegram,
    NotificacaoTelegram,
)


@admin.register(ConfiguracaoTelegram)
class ConfiguracaoTelegramAdmin(admin.ModelAdmin):
    list_display = (
        "id_configuracao",
        "aluno",
        "telegram_ativo",
        "telegram_username",
        "data_conexao",
    )
    list_filter = ("telegram_ativo", "data_exclusao")


@admin.register(CodigoConexaoTelegram)
class CodigoConexaoTelegramAdmin(admin.ModelAdmin):
    list_display = ("codigo", "aluno", "utilizado", "data_expiracao")
    list_filter = ("utilizado",)


@admin.register(NotificacaoTelegram)
class NotificacaoTelegramAdmin(admin.ModelAdmin):
    list_display = ("id_notificacao", "aluno", "tarefa", "tipo", "status_envio", "data_envio")
    list_filter = ("tipo", "status_envio")
