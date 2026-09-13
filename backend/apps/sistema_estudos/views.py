from datetime import timedelta

from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.sistema_estudos.models import Disciplina, LogAtividade, SessaoEstudo, SessaoPlanejada, Tarefa
from apps.sistema_estudos.querysets import disciplinas_ativas_com_metricas
from apps.sistema_estudos.serializers import (
    DisciplinaReadSerializer,
    DisciplinaWriteSerializer,
    SessaoEstudoReadSerializer,
    SessaoEstudoWriteSerializer,
    SessaoPlanejadaReadSerializer,
    SessaoPlanejadaWriteSerializer,
    TarefaReadSerializer,
    TarefaWriteSerializer,
)
from apps.sistema_estudos.services.feriados_service import intervalo_mes, listar_feriados_mes


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


class SessaoEstudoResumoAPIView(APIView):
    """Métricas do topo da tela de sessões de estudo."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        aluno = request.user
        hoje = timezone.localdate()
        base = SessaoEstudo.objects.filter(aluno=aluno, data_exclusao__isnull=True)
        total_horas_agg = base.aggregate(total=Sum("tempo_estudo"))
        total_horas = float(total_horas_agg["total"] or 0)
        sessoes_hoje = base.filter(data_sessao=hoje).count()
        total_sessoes = base.count()
        return Response(
            {
                "total_horas": round(total_horas, 1),
                "sessoes_hoje": sessoes_hoje,
                "total_sessoes": total_sessoes,
            }
        )


META_SEMANAL_HORAS = 10


class RelatoriosResumoAPIView(APIView):
    """Métricas e gráficos da tela de relatórios."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        aluno = request.user
        hoje = timezone.localdate()
        inicio_semana = hoje - timedelta(days=hoje.weekday())

        base_sessoes = SessaoEstudo.objects.filter(
            aluno=aluno, data_exclusao__isnull=True
        )
        total_horas = float(
            base_sessoes.aggregate(total=Sum("tempo_estudo"))["total"] or 0
        )

        disciplinas = list(disciplinas_ativas_com_metricas(aluno))
        qtd_disc = len(disciplinas)
        media_disc = round(total_horas / qtd_disc, 1) if qtd_disc else 0.0

        melhor_nome = "—"
        melhor_horas = 0.0
        distribuicao = []
        tempo_disciplinas = []

        for disc in disciplinas:
            horas = float(disc.horas_estudadas or 0)
            if horas > melhor_horas:
                melhor_horas = horas
                melhor_nome = disc.nome or "—"
            if horas > 0:
                item = {
                    "disciplina": disc.nome or "Disciplina",
                    "horas": round(horas, 1),
                }
                distribuicao.append(item)
                tempo_disciplinas.append(item)

        tempo_disciplinas.sort(key=lambda x: x["horas"], reverse=True)

        horas_semana = float(
            base_sessoes.filter(
                data_sessao__gte=inicio_semana,
                data_sessao__lte=hoje,
            ).aggregate(total=Sum("tempo_estudo"))["total"]
            or 0
        )
        meta_pct = (
            min(100, round(horas_semana / META_SEMANAL_HORAS * 100))
            if META_SEMANAL_HORAS
            else 0
        )

        dias_ordem = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        horas_por_dia = [0.0] * 7
        for sessao in base_sessoes.filter(
            data_sessao__gte=inicio_semana,
            data_sessao__lte=hoje,
        ).only("data_sessao", "tempo_estudo"):
            if sessao.data_sessao:
                horas_por_dia[sessao.data_sessao.weekday()] += float(
                    sessao.tempo_estudo or 0
                )

        grafico_semana = [
            {"dia": dias_ordem[i], "horas": round(horas_por_dia[i], 1)}
            for i in range(7)
        ]

        evolucao = []
        for offset in range(3, -1, -1):
            inicio = inicio_semana - timedelta(weeks=offset)
            fim = inicio + timedelta(days=6)
            horas = float(
                base_sessoes.filter(
                    data_sessao__gte=inicio,
                    data_sessao__lte=fim,
                ).aggregate(total=Sum("tempo_estudo"))["total"]
                or 0
            )
            evolucao.append(
                {"semana": f"Sem {4 - offset}", "horas": round(horas, 1)}
            )

        return Response(
            {
                "total_horas": round(total_horas, 1),
                "media_por_disciplina": media_disc,
                "melhor_disciplina": melhor_nome,
                "melhor_disciplina_horas": round(melhor_horas, 1),
                "meta_semanal_pct": meta_pct,
                "meta_semanal_horas": META_SEMANAL_HORAS,
                "horas_estudadas_semana": round(horas_semana, 1),
                "grafico_horas_semana": grafico_semana,
                "distribuicao_disciplinas": distribuicao,
                "evolucao_semanal": evolucao,
                "tempo_por_disciplina": tempo_disciplinas,
            }
        )


class SessaoEstudoListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            SessaoEstudo.objects.filter(
                aluno=self.request.user,
                data_exclusao__isnull=True,
            )
            .select_related("disciplina")
            .order_by("-data_sessao", "-id_sessao_estudo")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SessaoEstudoWriteSerializer
        return SessaoEstudoReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = SessaoEstudoWriteSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        sessao = serializer.save()
        sessao = self.get_queryset().get(pk=sessao.pk)
        return Response(
            SessaoEstudoReadSerializer(sessao).data,
            status=status.HTTP_201_CREATED,
        )


class CalendarioAPIView(APIView):
    """Dados do calendário de estudos: tarefas, sessões e feriados do mês."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        aluno = request.user
        hoje = timezone.localdate()

        try:
            ano = int(request.query_params.get("ano", hoje.year))
            mes = int(request.query_params.get("mes", hoje.month))
        except (TypeError, ValueError):
            return Response(
                {"detail": "Parâmetros ano e mes devem ser números inteiros."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if mes < 1 or mes > 12 or ano < 2000 or ano > 2100:
            return Response(
                {"detail": "Ano ou mês inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        inicio, fim = intervalo_mes(ano, mes)

        tarefas = (
            Tarefa.objects.filter(
                disciplina__aluno=aluno,
                disciplina__data_exclusao__isnull=True,
                data_exclusao__isnull=True,
                data_entrega__gte=inicio,
                data_entrega__lte=fim,
            )
            .select_related("disciplina")
            .order_by("data_entrega", "id_tarefa")
        )

        sessoes_planejadas = (
            SessaoPlanejada.objects.filter(
                aluno=aluno,
                data_exclusao__isnull=True,
                data_planejada__gte=inicio,
                data_planejada__lte=fim,
            )
            .select_related("disciplina")
            .order_by("data_planejada", "id_sessao_planejada")
        )

        sessoes_realizadas = (
            SessaoEstudo.objects.filter(
                aluno=aluno,
                data_exclusao__isnull=True,
                data_sessao__gte=inicio,
                data_sessao__lte=fim,
            )
            .select_related("disciplina")
            .order_by("data_sessao", "id_sessao_estudo")
        )

        feriados = listar_feriados_mes(ano, mes)

        return Response(
            {
                "ano": ano,
                "mes": mes,
                "feriados": feriados,
                "tarefas": TarefaReadSerializer(tarefas, many=True).data,
                "sessoes_planejadas": SessaoPlanejadaReadSerializer(
                    sessoes_planejadas, many=True
                ).data,
                "sessoes_realizadas": SessaoEstudoReadSerializer(
                    sessoes_realizadas, many=True
                ).data,
            }
        )


class TarefaListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        aluno = self.request.user
        qs = Tarefa.objects.filter(
            disciplina__aluno=aluno,
            disciplina__data_exclusao__isnull=True,
            data_exclusao__isnull=True,
        ).select_related("disciplina")

        de = self.request.query_params.get("de")
        ate = self.request.query_params.get("ate")
        if de:
            qs = qs.filter(data_entrega__gte=de)
        if ate:
            qs = qs.filter(data_entrega__lte=ate)

        return qs.order_by("data_entrega", "id_tarefa")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TarefaWriteSerializer
        return TarefaReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = TarefaWriteSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        tarefa = serializer.save()
        tarefa = self.get_queryset().get(pk=tarefa.pk)
        return Response(
            TarefaReadSerializer(tarefa).data,
            status=status.HTTP_201_CREATED,
        )


class TarefaDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        return Tarefa.objects.filter(
            disciplina__aluno=self.request.user,
            disciplina__data_exclusao__isnull=True,
            data_exclusao__isnull=True,
        ).select_related("disciplina")

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return TarefaWriteSerializer
        return TarefaReadSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = TarefaWriteSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        refreshed = self.get_queryset().get(pk=instance.pk)
        return Response(TarefaReadSerializer(refreshed).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.data_exclusao = timezone.now()
        instance.save(update_fields=["data_exclusao"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessaoPlanejadaListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = SessaoPlanejada.objects.filter(
            aluno=self.request.user,
            data_exclusao__isnull=True,
        ).select_related("disciplina")

        de = self.request.query_params.get("de")
        ate = self.request.query_params.get("ate")
        if de:
            qs = qs.filter(data_planejada__gte=de)
        if ate:
            qs = qs.filter(data_planejada__lte=ate)

        return qs.order_by("data_planejada", "id_sessao_planejada")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SessaoPlanejadaWriteSerializer
        return SessaoPlanejadaReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = SessaoPlanejadaWriteSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        sessao = serializer.save()
        sessao = self.get_queryset().get(pk=sessao.pk)
        return Response(
            SessaoPlanejadaReadSerializer(sessao).data,
            status=status.HTTP_201_CREATED,
        )


class SessaoPlanejadaDetailAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        return SessaoPlanejada.objects.filter(
            aluno=self.request.user,
            data_exclusao__isnull=True,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.data_exclusao = timezone.now()
        instance.save(update_fields=["data_exclusao"])
        return Response(status=status.HTTP_204_NO_CONTENT)
