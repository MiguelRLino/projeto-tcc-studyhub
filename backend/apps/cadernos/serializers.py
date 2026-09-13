from rest_framework import serializers

from apps.cadernos.models import Caderno, ImagemCaderno, PaginaCaderno
from apps.cadernos.utils import (
    calcular_metricas_conteudo,
    conteudo_vazio,
    normalizar_conteudo,
    tempo_leitura_minutos,
)
from apps.sistema_estudos.models import Disciplina


class CadernoWriteSerializer(serializers.ModelSerializer):
    id_disciplina = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Caderno
        fields = (
            "titulo",
            "descricao",
            "cor",
            "icone",
            "ordem",
            "id_disciplina",
        )

    def validate_titulo(self, value):
        if not str(value or "").strip():
            raise serializers.ValidationError("Informe o título do caderno.")
        return str(value).strip()[:150]

    def validate_id_disciplina(self, value):
        if value is None:
            return None
        aluno = self.context["request"].user
        if not Disciplina.objects.filter(
            pk=value, aluno=aluno, data_exclusao__isnull=True
        ).exists():
            raise serializers.ValidationError("Disciplina inválida ou não encontrada.")
        return value

    def create(self, validated_data):
        disciplina_id = validated_data.pop("id_disciplina", None)
        aluno = self.context["request"].user
        return Caderno.objects.create(
            aluno=aluno,
            disciplina_id=disciplina_id,
            **validated_data,
        )

    def update(self, instance, validated_data):
        disciplina_id = validated_data.pop("id_disciplina", serializers.empty)
        if disciplina_id is not serializers.empty:
            instance.disciplina_id = disciplina_id
        for field in ("titulo", "descricao", "cor", "icone", "ordem"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance


class CadernoReadSerializer(serializers.ModelSerializer):
    id_disciplina = serializers.IntegerField(
        source="disciplina_id", read_only=True, allow_null=True
    )
    disciplina_nome = serializers.SerializerMethodField()
    total_paginas = serializers.SerializerMethodField()

    class Meta:
        model = Caderno
        fields = (
            "id_caderno",
            "titulo",
            "descricao",
            "cor",
            "icone",
            "ordem",
            "id_disciplina",
            "disciplina_nome",
            "total_paginas",
            "data_criacao",
            "data_atualizacao",
        )

    def get_disciplina_nome(self, obj):
        if obj.disciplina_id and obj.disciplina:
            return obj.disciplina.nome
        return ""

    def get_total_paginas(self, obj):
        return obj.paginas.filter(data_exclusao__isnull=True).count()


class PaginaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaginaCaderno
        fields = ("titulo", "conteudo", "ordem", "favorita")

    def validate_titulo(self, value):
        if not str(value or "").strip():
            raise serializers.ValidationError("Informe o título da página.")
        return str(value).strip()[:200]

    def validate_conteudo(self, value):
        return normalizar_conteudo(value)

    def create(self, validated_data):
        caderno = self.context["caderno"]
        conteudo = validated_data.get("conteudo") or conteudo_vazio()
        palavras, caracteres = calcular_metricas_conteudo(conteudo)
        if "ordem" not in validated_data:
            ultima = (
                caderno.paginas.filter(data_exclusao__isnull=True)
                .order_by("-ordem")
                .values_list("ordem", flat=True)
                .first()
            )
            validated_data["ordem"] = (ultima or 0) + 1
        return PaginaCaderno.objects.create(
            caderno=caderno,
            quantidade_palavras=palavras,
            quantidade_caracteres=caracteres,
            **validated_data,
        )

    def update(self, instance, validated_data):
        if "conteudo" in validated_data:
            conteudo = normalizar_conteudo(validated_data["conteudo"])
            validated_data["conteudo"] = conteudo
            palavras, caracteres = calcular_metricas_conteudo(conteudo)
            instance.quantidade_palavras = palavras
            instance.quantidade_caracteres = caracteres
        for field in ("titulo", "conteudo", "ordem", "favorita"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance


class PaginaReadSerializer(serializers.ModelSerializer):
    id_caderno = serializers.IntegerField(source="caderno_id", read_only=True)
    caderno_titulo = serializers.SerializerMethodField()
    tempo_leitura_min = serializers.SerializerMethodField()

    class Meta:
        model = PaginaCaderno
        fields = (
            "id_pagina",
            "id_caderno",
            "caderno_titulo",
            "titulo",
            "conteudo",
            "ordem",
            "favorita",
            "quantidade_palavras",
            "quantidade_caracteres",
            "tempo_leitura_min",
            "data_criacao",
            "data_atualizacao",
        )

    def get_caderno_titulo(self, obj):
        return obj.caderno.titulo if obj.caderno else ""

    def get_tempo_leitura_min(self, obj):
        return tempo_leitura_minutos(obj.quantidade_palavras or 0)


class PaginaResumoSerializer(serializers.ModelSerializer):
    id_caderno = serializers.IntegerField(source="caderno_id", read_only=True)
    caderno_titulo = serializers.SerializerMethodField()

    class Meta:
        model = PaginaCaderno
        fields = (
            "id_pagina",
            "id_caderno",
            "caderno_titulo",
            "titulo",
            "ordem",
            "favorita",
            "quantidade_palavras",
            "data_atualizacao",
        )

    def get_caderno_titulo(self, obj):
        return obj.caderno.titulo if obj.caderno else ""


class MoverPaginaSerializer(serializers.Serializer):
    caderno_destino_id = serializers.IntegerField()

    def validate_caderno_destino_id(self, value):
        aluno = self.context["request"].user
        if not Caderno.objects.filter(
            pk=value, aluno=aluno, data_exclusao__isnull=True
        ).exists():
            raise serializers.ValidationError("Caderno de destino inválido.")
        return value


class ReordenarPaginasSerializer(serializers.Serializer):
    ordens = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False,
    )

    def validate_ordens(self, value):
        for item in value:
            if "id_pagina" not in item or "ordem" not in item:
                raise serializers.ValidationError(
                    "Cada item deve conter id_pagina e ordem."
                )
        return value


class ImagemCadernoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ImagemCaderno
        fields = ("id_imagem", "url", "nome_original", "data_upload")

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.arquivo and request:
            return request.build_absolute_uri(obj.arquivo.url)
        if obj.arquivo:
            return obj.arquivo.url
        return ""
