from decimal import Decimal

from rest_framework import serializers

from apps.sistema_estudos.models import Disciplina, SessaoEstudo, SessaoPlanejada, Tarefa


class DisciplinaWriteSerializer(serializers.ModelSerializer):
    """Campos enviados em POST/PATCH (sem métricas agregadas)."""

    class Meta:
        model = Disciplina
        fields = ("nome", "nivel_dificuldade")

    def validate_nome(self, value: str) -> str:
        if value is None or not str(value).strip():
            raise serializers.ValidationError("Nome é obrigatório.")
        return str(value).strip()

    def validate_nivel_dificuldade(self, value):
        if value is None:
            return value
        try:
            v = int(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Informe um número inteiro.")
        if v < 1 or v > 5:
            raise serializers.ValidationError("Nível de dificuldade deve estar entre 1 e 5.")
        return v


class DisciplinaReadSerializer(serializers.ModelSerializer):
    """Leitura com métricas vindas do queryset anotado."""

    horas_estudadas = serializers.SerializerMethodField()
    tarefas_pendentes = serializers.SerializerMethodField()

    class Meta:
        model = Disciplina
        fields = (
            "id_disciplina",
            "nome",
            "nivel_dificuldade",
            "data_exclusao",
            "horas_estudadas",
            "tarefas_pendentes",
        )

    def get_horas_estudadas(self, obj):
        v = getattr(obj, "horas_estudadas", None)
        if v is None:
            return 0.0
        return round(float(v), 2)

    def get_tarefas_pendentes(self, obj):
        return int(getattr(obj, "tarefas_pendentes", 0) or 0)


class SessaoEstudoWriteSerializer(serializers.ModelSerializer):
    id_disciplina = serializers.IntegerField()

    class Meta:
        model = SessaoEstudo
        fields = ("id_disciplina", "tempo_estudo", "data_sessao")

    def validate_id_disciplina(self, value):
        aluno = self.context["request"].user
        if not Disciplina.objects.filter(
            pk=value, aluno=aluno, data_exclusao__isnull=True
        ).exists():
            raise serializers.ValidationError("Disciplina inválida ou não encontrada.")
        return value

    def validate_tempo_estudo(self, value):
        if value is None:
            raise serializers.ValidationError("Informe a duração da sessão.")
        try:
            horas = Decimal(str(value))
        except Exception:
            raise serializers.ValidationError("Duração inválida.")
        if horas <= 0:
            raise serializers.ValidationError("A duração deve ser maior que zero.")
        if horas > Decimal("999.99"):
            raise serializers.ValidationError("Duração acima do limite permitido.")
        return horas.quantize(Decimal("0.01"))

    def create(self, validated_data):
        from django.utils import timezone

        aluno = self.context["request"].user
        disciplina_id = validated_data.pop("id_disciplina")
        data_sessao = validated_data.get("data_sessao") or timezone.localdate()
        return SessaoEstudo.objects.create(
            aluno=aluno,
            disciplina_id=disciplina_id,
            tempo_estudo=validated_data["tempo_estudo"],
            data_sessao=data_sessao,
        )


class SessaoEstudoReadSerializer(serializers.ModelSerializer):
    id_disciplina = serializers.IntegerField(
        source="disciplina_id", read_only=True, allow_null=True
    )
    disciplina_nome = serializers.SerializerMethodField()

    class Meta:
        model = SessaoEstudo
        fields = (
            "id_sessao_estudo",
            "id_disciplina",
            "disciplina_nome",
            "tempo_estudo",
            "data_sessao",
        )

    def get_disciplina_nome(self, obj):
        if obj.disciplina_id and obj.disciplina:
            return obj.disciplina.nome
        return ""


class TarefaWriteSerializer(serializers.ModelSerializer):
    id_disciplina = serializers.IntegerField(required=False)

    class Meta:
        model = Tarefa
        fields = ("id_disciplina", "descricao", "data_entrega", "hora_entrega", "status_tarefa")

    def validate_id_disciplina(self, value):
        aluno = self.context["request"].user
        if not Disciplina.objects.filter(
            pk=value, aluno=aluno, data_exclusao__isnull=True
        ).exists():
            raise serializers.ValidationError("Disciplina inválida ou não encontrada.")
        return value

    def validate_descricao(self, value):
        if value is None or not str(value).strip():
            raise serializers.ValidationError("Descrição é obrigatória.")
        return str(value).strip()

    def validate(self, attrs):
        if self.instance is None and attrs.get("id_disciplina") is None:
            raise serializers.ValidationError(
                {"id_disciplina": "Informe a disciplina da tarefa."}
            )
        return attrs

    def create(self, validated_data):
        disciplina_id = validated_data.pop("id_disciplina")
        return Tarefa.objects.create(
            disciplina_id=disciplina_id,
            descricao=validated_data["descricao"],
            data_entrega=validated_data.get("data_entrega"),
            hora_entrega=validated_data.get("hora_entrega"),
            status_tarefa=validated_data.get("status_tarefa") or "pendente",
        )

    def update(self, instance, validated_data):
        disciplina_id = validated_data.pop("id_disciplina", None)
        if disciplina_id is not None:
            instance.disciplina_id = disciplina_id
        for field in ("descricao", "data_entrega", "hora_entrega", "status_tarefa"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance


class TarefaReadSerializer(serializers.ModelSerializer):
    id_disciplina = serializers.IntegerField(
        source="disciplina_id", read_only=True, allow_null=True
    )
    disciplina_nome = serializers.SerializerMethodField()
    concluida = serializers.SerializerMethodField()
    atrasada = serializers.SerializerMethodField()

    class Meta:
        model = Tarefa
        fields = (
            "id_tarefa",
            "id_disciplina",
            "disciplina_nome",
            "descricao",
            "data_entrega",
            "hora_entrega",
            "status_tarefa",
            "concluida",
            "atrasada",
        )

    def get_disciplina_nome(self, obj):
        if obj.disciplina_id and obj.disciplina:
            return obj.disciplina.nome
        return ""

    def _status_normalizado(self, obj):
        return (obj.status_tarefa or "").strip().lower()

    def get_concluida(self, obj):
        return self._status_normalizado(obj) in (
            "concluida",
            "concluída",
            "concluido",
            "concluído",
            "feito",
            "done",
        )

    def get_atrasada(self, obj):
        if self.get_concluida(obj) or not obj.data_entrega:
            return False
        from django.utils import timezone

        return obj.data_entrega < timezone.localdate()


class SessaoPlanejadaWriteSerializer(serializers.ModelSerializer):
    id_disciplina = serializers.IntegerField()

    class Meta:
        model = SessaoPlanejada
        fields = (
            "id_disciplina",
            "data_planejada",
            "duracao_prevista_minutos",
            "observacao",
        )

    def validate_id_disciplina(self, value):
        aluno = self.context["request"].user
        if not Disciplina.objects.filter(
            pk=value, aluno=aluno, data_exclusao__isnull=True
        ).exists():
            raise serializers.ValidationError("Disciplina inválida ou não encontrada.")
        return value

    def validate_data_planejada(self, value):
        if value is None:
            raise serializers.ValidationError("Informe a data da sessão planejada.")
        return value

    def validate_duracao_prevista_minutos(self, value):
        if value is None:
            return value
        if value <= 0:
            raise serializers.ValidationError("A duração deve ser maior que zero.")
        if value > 24 * 60:
            raise serializers.ValidationError("Duração acima do limite permitido.")
        return value

    def create(self, validated_data):
        aluno = self.context["request"].user
        disciplina_id = validated_data.pop("id_disciplina")
        return SessaoPlanejada.objects.create(
            aluno=aluno,
            disciplina_id=disciplina_id,
            data_planejada=validated_data["data_planejada"],
            duracao_prevista_minutos=validated_data.get("duracao_prevista_minutos"),
            observacao=validated_data.get("observacao") or "",
        )


class SessaoPlanejadaReadSerializer(serializers.ModelSerializer):
    id_disciplina = serializers.IntegerField(
        source="disciplina_id", read_only=True, allow_null=True
    )
    disciplina_nome = serializers.SerializerMethodField()

    class Meta:
        model = SessaoPlanejada
        fields = (
            "id_sessao_planejada",
            "id_disciplina",
            "disciplina_nome",
            "data_planejada",
            "duracao_prevista_minutos",
            "observacao",
        )

    def get_disciplina_nome(self, obj):
        if obj.disciplina_id and obj.disciplina:
            return obj.disciplina.nome
        return ""
