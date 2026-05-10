from django.urls import path

from apps.sistema_estudos.views import (
    DashboardResumoAPIView,
    DisciplinaDetailAPIView,
    DisciplinaListCreateAPIView,
)

urlpatterns = [
    path("dashboard/resumo/", DashboardResumoAPIView.as_view(), name="dashboard-resumo"),
    path("disciplinas/", DisciplinaListCreateAPIView.as_view(), name="disciplina-list-create"),
    path(
        "disciplinas/<int:pk>/",
        DisciplinaDetailAPIView.as_view(),
        name="disciplina-detail",
    ),
]
