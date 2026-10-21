from django.urls import path

from apps.responsaveis import views

urlpatterns = [
    path("convidar/", views.ConvidarResponsavelAPIView.as_view(), name="resp-convidar"),
    path(
        "meus-responsaveis/",
        views.MeusResponsaveisAPIView.as_view(),
        name="resp-meus-responsaveis",
    ),
    path(
        "convites/<int:convite_id>/reenviar/",
        views.ReenviarConviteAPIView.as_view(),
        name="resp-reenviar",
    ),
    path(
        "convites/<int:convite_id>/",
        views.CancelarConviteAPIView.as_view(),
        name="resp-cancelar-convite",
    ),
    path(
        "vinculos/<int:vinculo_id>/",
        views.RemoverVinculoAPIView.as_view(),
        name="resp-remover-vinculo",
    ),
    path(
        "convites/validar/<str:token>/",
        views.ValidarConviteAPIView.as_view(),
        name="resp-validar",
    ),
    path(
        "convites/aceitar/",
        views.AceitarConviteAPIView.as_view(),
        name="resp-aceitar",
    ),
    path("meus-alunos/", views.MeusAlunosAPIView.as_view(), name="resp-meus-alunos"),
    path(
        "alunos/<int:aluno_id>/dashboard/",
        views.ResponsavelAlunoDashboardAPIView.as_view(),
        name="resp-aluno-dashboard",
    ),
    path(
        "alunos/<int:aluno_id>/tarefas/",
        views.ResponsavelAlunoTarefasAPIView.as_view(),
        name="resp-aluno-tarefas",
    ),
    path(
        "alunos/<int:aluno_id>/disciplinas/",
        views.ResponsavelAlunoDisciplinasAPIView.as_view(),
        name="resp-aluno-disciplinas",
    ),
    path(
        "alunos/<int:aluno_id>/sessoes/",
        views.ResponsavelAlunoSessoesAPIView.as_view(),
        name="resp-aluno-sessoes",
    ),
    path(
        "alunos/<int:aluno_id>/relatorios/",
        views.ResponsavelAlunoRelatoriosAPIView.as_view(),
        name="resp-aluno-relatorios",
    ),
    path("login/", views.ResponsavelLoginAPIView.as_view(), name="resp-login"),
]
