from django.urls import path

from apps.sistema_estudos.views import (
    CalendarioAPIView,
    DashboardResumoAPIView,
    DisciplinaDetailAPIView,
    DisciplinaListCreateAPIView,
    RelatoriosResumoAPIView,
    SessaoEstudoListCreateAPIView,
    SessaoEstudoResumoAPIView,
    SessaoPlanejadaDetailAPIView,
    SessaoPlanejadaListCreateAPIView,
    TarefaDetailAPIView,
    TarefaListCreateAPIView,
)

urlpatterns = [
    path("dashboard/resumo/", DashboardResumoAPIView.as_view(), name="dashboard-resumo"),
    path("relatorios/resumo/", RelatoriosResumoAPIView.as_view(), name="relatorios-resumo"),
    path("disciplinas/", DisciplinaListCreateAPIView.as_view(), name="disciplina-list-create"),
    path(
        "disciplinas/<int:pk>/",
        DisciplinaDetailAPIView.as_view(),
        name="disciplina-detail",
    ),
    path(
        "sessoes-estudo/resumo/",
        SessaoEstudoResumoAPIView.as_view(),
        name="sessao-estudo-resumo",
    ),
    path(
        "sessoes-estudo/",
        SessaoEstudoListCreateAPIView.as_view(),
        name="sessao-estudo-list-create",
    ),
    path("calendario/", CalendarioAPIView.as_view(), name="calendario"),
    path("tarefas/", TarefaListCreateAPIView.as_view(), name="tarefa-list-create"),
    path(
        "tarefas/<int:pk>/",
        TarefaDetailAPIView.as_view(),
        name="tarefa-detail",
    ),
    path(
        "sessoes-planejadas/",
        SessaoPlanejadaListCreateAPIView.as_view(),
        name="sessao-planejada-list-create",
    ),
    path(
        "sessoes-planejadas/<int:pk>/",
        SessaoPlanejadaDetailAPIView.as_view(),
        name="sessao-planejada-detail",
    ),
]
