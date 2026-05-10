from datetime import timedelta

from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.sistema_estudos.models import Disciplina, LogAtividade, SessaoEstudo, Tarefa
from apps.sistema_estudos.querysets import disciplinas_ativas_com_metricas
from apps.sistema_estudos.serializers import DisciplinaReadSerializer, DisciplinaWriteSerializer


class DashboardResumoAPIView(APIView):
    """Resumo para o dashboard (métricas reais quando houver dados nas tabelas)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        aluno = request.user

        disciplinas_ativas = Disciplina.objects.filter(
            aluno=aluno, data_exclusao__isnull=True
        ).count()

        tarefas_qs = Tarefa.objects.filter(
            disciplina__aluno=aluno,
            disciplina__data_exclusao__isnull=True,
            data_exclusao__isnull=True,
        )
        concluido_q = (
            Q(status_tarefa__iexact="concluida")
            | Q(status_tarefa__iexact="concluída")
            | Q(status_tarefa__iexact="concluido")
            | Q(status_tarefa__iexact="concluído")
            | Q(status_tarefa__iexact="feito")
            | Q(status_tarefa__iexact="done")
        )
        tarefas_pendentes = tarefas_qs.exclude(concluido_q).count()

        hoje = timezone.localdate()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        horas_semana_agg = SessaoEstudo.objects.filter(
            aluno=aluno,
            data_exclusao__isnull=True,
            data_sessao__gte=inicio_semana,
            data_sessao__lte=hoje,
        ).aggregate(total=Sum("tempo_estudo"))
        horas_semana = float(horas_semana_agg["total"] or 0)

        dias_ordem = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        horas_por_dia = [0.0] * 7
        sessoes = SessaoEstudo.objects.filter(
            aluno=aluno,
            data_exclusao__isnull=True,
            data_sessao__gte=hoje - timedelta(days=13),
        ).only("data_sessao", "tempo_estudo")

        for s in sessoes:
            if not s.data_sessao:
                continue
            wd = s.data_sessao.weekday()
            horas_por_dia[wd] += float(s.tempo_estudo or 0)

        atividades = []
        for log in LogAtividade.objects.filter(aluno=aluno).order_by("-data_hora")[:8]:
            atividades.append(
                {
                    "descricao": log.descricao or log.acao or "Atividade",
                    "acao": log.acao,
                    "quando": log.data_hora.isoformat() if log.data_hora else None,
                    "rotulo": log.tabela_afetada or "",
                }
            )

        proxima_info = None
        proxima = (
            Tarefa.objects.filter(
                disciplina__aluno=aluno,
                disciplina__data_exclusao__isnull=True,
                data_exclusao__isnull=True,
                data_entrega__gte=hoje,
            )
            .select_related("disciplina")
            .order_by("data_entrega")
            .first()
        )
        if proxima and proxima.data_entrega:
            dias = (proxima.data_entrega - hoje).days
            proxima_info = {
                "dias": dias,
                "titulo": (proxima.descricao or "Tarefa")[:80],
                "disciplina": proxima.disciplina.nome if proxima.disciplina else "",
            }

        prioritarias = Disciplina.objects.filter(
            aluno=aluno,
            data_exclusao__isnull=True,
            nivel_dificuldade__gte=4,
        ).count()

        return Response(
            {
                "disciplinas_ativas": disciplinas_ativas,
                "disciplinas_prioridade_alta": prioritarias,
                "tarefas_pendentes": tarefas_pendentes,
                "horas_estudadas_semana": round(horas_semana, 2),
                "grafico_horas_semana": [
                    {"dia": dias_ordem[i], "horas": round(horas_por_dia[i], 2)}
                    for i in range(7)
                ],
                "atividades_recentes": atividades,
                "proxima_entrega": proxima_info,
            }
        )


class DisciplinaListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return disciplinas_ativas_com_metricas(self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return DisciplinaWriteSerializer
        return DisciplinaReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = DisciplinaWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        disciplina = serializer.save(aluno=request.user)
        refreshed = disciplinas_ativas_com_metricas(request.user).get(pk=disciplina.pk)
        return Response(
            DisciplinaReadSerializer(refreshed).data,
            status=status.HTTP_201_CREATED,
        )


class DisciplinaDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        return disciplinas_ativas_com_metricas(self.request.user)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return DisciplinaWriteSerializer
        return DisciplinaReadSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = DisciplinaWriteSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        refreshed = disciplinas_ativas_com_metricas(request.user).get(pk=instance.pk)
        return Response(DisciplinaReadSerializer(refreshed).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.data_exclusao = timezone.now()
        instance.save(update_fields=["data_exclusao"])
        return Response(status=status.HTTP_204_NO_CONTENT)
