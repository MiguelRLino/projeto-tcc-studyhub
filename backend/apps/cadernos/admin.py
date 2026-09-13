from django.contrib import admin

from apps.cadernos.models import Caderno, ImagemCaderno, PaginaCaderno


@admin.register(Caderno)
class CadernoAdmin(admin.ModelAdmin):
    list_display = ("id_caderno", "titulo", "aluno", "disciplina", "data_exclusao")


@admin.register(PaginaCaderno)
class PaginaCadernoAdmin(admin.ModelAdmin):
    list_display = ("id_pagina", "titulo", "caderno", "favorita", "data_exclusao")


@admin.register(ImagemCaderno)
class ImagemCadernoAdmin(admin.ModelAdmin):
    list_display = ("id_imagem", "pagina", "nome_original", "data_upload")
