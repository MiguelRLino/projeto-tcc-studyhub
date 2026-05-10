from django.urls import path

from apps.alunos.views import (
    AlunoCadastroView,
    AlunoGoogleLoginView,
    AlunoLoginView,
    AlunoPerfilView,
)

urlpatterns = [
    path("cadastro/", AlunoCadastroView.as_view(), name="aluno-cadastro"),
    path("login/", AlunoLoginView.as_view(), name="aluno-login"),
    path("login/google/", AlunoGoogleLoginView.as_view(), name="aluno-login-google"),
    path("me/", AlunoPerfilView.as_view(), name="aluno-perfil"),
]
