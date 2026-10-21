from django.contrib import admin

from apps.responsaveis.models import ConviteResponsavel, Responsavel, ResponsavelAluno


@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ("id_responsavel", "nome", "email", "data_criacao")
    search_fields = ("nome", "email")


@admin.register(ConviteResponsavel)
class ConviteResponsavelAdmin(admin.ModelAdmin):
    list_display = (
        "id_convite",
        "nome_convidado",
        "email_convidado",
        "parentesco",
        "status",
        "data_expiracao",
    )
    list_filter = ("status", "parentesco")
    search_fields = ("email_convidado", "nome_convidado")


@admin.register(ResponsavelAluno)
class ResponsavelAlunoAdmin(admin.ModelAdmin):
    list_display = (
        "id_vinculo",
        "aluno",
        "responsavel",
        "parentesco",
        "status",
        "data_aceitacao",
    )
    list_filter = ("status", "parentesco")
