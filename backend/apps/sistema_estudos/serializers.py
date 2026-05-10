from rest_framework import serializers

from apps.sistema_estudos.models import Disciplina


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
