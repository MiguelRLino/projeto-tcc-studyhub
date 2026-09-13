from django.urls import path

from apps.alunos.views import (
    AlunoAlterarSenhaView,
    AlunoCadastroView,
    AlunoGoogleLoginView,
    AlunoLoginView,
    AlunoPerfilView,
    AlunoRecuperarSenhaConfirmarView,
    AlunoRecuperarSenhaSolicitarView,
)

urlpatterns = [
    path("cadastro/", AlunoCadastroView.as_view(), name="aluno-cadastro"),
    path("login/", AlunoLoginView.as_view(), name="aluno-login"),
    path("login/google/", AlunoGoogleLoginView.as_view(), name="aluno-login-google"),
    path(
        "recuperar-senha/solicitar/",
        AlunoRecuperarSenhaSolicitarView.as_view(),
        name="aluno-recuperar-senha-solicitar",
    ),
    path(
        "recuperar-senha/confirmar/",
        AlunoRecuperarSenhaConfirmarView.as_view(),
        name="aluno-recuperar-senha-confirmar",
    ),
    path("me/", AlunoPerfilView.as_view(), name="aluno-perfil"),
    path("me/senha/", AlunoAlterarSenhaView.as_view(), name="aluno-alterar-senha"),
]
