from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.hashers import make_password
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.alunos.models import Aluno
from apps.alunos.services.auth_service import TIPO_RESPONSAVEL, criar_token_acesso
from apps.responsaveis.models import (
    ConviteResponsavel,
    Responsavel,
    ResponsavelAluno,
    StatusConvite,
    StatusVinculo,
)
from apps.responsaveis.services import (
    _hash_token,
    gerar_token_convite,
)
from apps.sistema_estudos.models import Disciplina, Tarefa


@override_settings(
    DEBUG=True,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    FRONTEND_URL="http://localhost:5173",
)
class ResponsaveisFluxoTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.aluno = Aluno.objects.create(
            nome="João Aluno",
            email="joao@teste.com",
            senha=make_password("senha12345"),
        )
        self.token_aluno = criar_token_acesso(self.aluno.id_aluno)

    def auth_aluno(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_aluno}")

    def test_aluno_envia_convite(self):
        self.auth_aluno()
        resp = self.client.post(
            "/api/responsaveis/convidar/",
            {
                "nome": "Maria Mãe",
                "email": "maria@teste.com",
                "parentesco": "MAE",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("StudyHub", mail.outbox[0].subject)
        self.assertTrue(
            ConviteResponsavel.objects.filter(
                email_convidado="maria@teste.com",
                status=StatusConvite.PENDENTE,
            ).exists()
        )

    def test_responsavel_nao_cadastra_publicamente(self):
        resp = self.client.post(
            "/api/alunos/cadastro/",
            {
                "nome": "Fake",
                "email": "fake@teste.com",
                "senha": "senha12345",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data.get("tipo"), "ALUNO")
        self.assertFalse(Responsavel.objects.filter(email="fake@teste.com").exists())

    def test_convite_valido_cria_conta(self):
        self.auth_aluno()
        criar = self.client.post(
            "/api/responsaveis/convidar/",
            {
                "nome": "Carlos Pai",
                "email": "carlos@teste.com",
                "parentesco": "PAI",
            },
            format="json",
        )
        token = criar.data["link_desenvolvimento"].rsplit("/", 1)[-1]
        self.client.credentials()
        aceitar = self.client.post(
            "/api/responsaveis/convites/aceitar/",
            {
                "token": token,
                "senha": "senha12345",
                "senha_confirmacao": "senha12345",
            },
            format="json",
        )
        self.assertEqual(aceitar.status_code, 200)
        self.assertEqual(aceitar.data["tipo"], TIPO_RESPONSAVEL)
        self.assertTrue(
            Responsavel.objects.filter(email="carlos@teste.com").exists()
        )
        self.assertTrue(
            ResponsavelAluno.objects.filter(
                aluno=self.aluno,
                status=StatusVinculo.ATIVO,
            ).exists()
        )

    def test_convite_expirado_recusado(self):
        token = gerar_token_convite()
        ConviteResponsavel.objects.create(
            aluno=self.aluno,
            nome_convidado="Exp",
            email_convidado="exp@teste.com",
            parentesco="OUTRO",
            token_hash=_hash_token(token),
            data_expiracao=timezone.now() - timedelta(hours=1),
            status=StatusConvite.PENDENTE,
        )
        resp = self.client.get(f"/api/responsaveis/convites/validar/{token}/")
        self.assertEqual(resp.status_code, 400)

    def test_convite_nao_reutilizavel(self):
        self.auth_aluno()
        criar = self.client.post(
            "/api/responsaveis/convidar/",
            {
                "nome": "Ana",
                "email": "ana@teste.com",
                "parentesco": "MAE",
            },
            format="json",
        )
        token = criar.data["link_desenvolvimento"].rsplit("/", 1)[-1]
        self.client.credentials()
        self.client.post(
            "/api/responsaveis/convites/aceitar/",
            {
                "token": token,
                "senha": "senha12345",
                "senha_confirmacao": "senha12345",
            },
            format="json",
        )
        segunda = self.client.post(
            "/api/responsaveis/convites/aceitar/",
            {
                "token": token,
                "senha": "senha12345",
                "senha_confirmacao": "senha12345",
            },
            format="json",
        )
        # Token é invalidado após aceite (hash rotacionado) → 404; ou 400 se ainda encontrado
        self.assertIn(segunda.status_code, (400, 404))

    def test_email_diferente_nao_aceita_logado(self):
        self.auth_aluno()
        criar = self.client.post(
            "/api/responsaveis/convidar/",
            {
                "nome": "Outro",
                "email": "outro@teste.com",
                "parentesco": "OUTRO",
            },
            format="json",
        )
        token = criar.data["link_desenvolvimento"].rsplit("/", 1)[-1]
        resp_user = Responsavel.objects.create(
            nome="Intruso",
            email="intruso@teste.com",
            senha=make_password("senha12345"),
        )
        tok = criar_token_acesso(
            tipo=TIPO_RESPONSAVEL,
            id_responsavel=resp_user.id_responsavel,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok}")
        aceitar = self.client.post(
            "/api/responsaveis/convites/aceitar/",
            {"token": token},
            format="json",
        )
        self.assertEqual(aceitar.status_code, 403)

    def test_responsavel_existente_aceita_novo_convite(self):
        responsavel = Responsavel.objects.create(
            nome="Maria",
            email="maria2@teste.com",
            senha=make_password("senha12345"),
        )
        self.auth_aluno()
        criar = self.client.post(
            "/api/responsaveis/convidar/",
            {
                "nome": "Maria",
                "email": "maria2@teste.com",
                "parentesco": "MAE",
            },
            format="json",
        )
        token = criar.data["link_desenvolvimento"].rsplit("/", 1)[-1]
        tok = criar_token_acesso(
            tipo=TIPO_RESPONSAVEL,
            id_responsavel=responsavel.id_responsavel,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok}")
        aceitar = self.client.post(
            "/api/responsaveis/convites/aceitar/",
            {"token": token},
            format="json",
        )
        self.assertEqual(aceitar.status_code, 200)
        self.assertEqual(
            ResponsavelAluno.objects.filter(
                responsavel=responsavel, status=StatusVinculo.ATIVO
            ).count(),
            1,
        )

    def test_multiplos_responsaveis_e_alunos(self):
        self.auth_aluno()
        for email, parentesco in [
            ("r1@teste.com", "MAE"),
            ("r2@teste.com", "PAI"),
        ]:
            self.client.post(
                "/api/responsaveis/convidar/",
                {"nome": email, "email": email, "parentesco": parentesco},
                format="json",
            )
        self.assertEqual(
            ConviteResponsavel.objects.filter(
                aluno=self.aluno, status=StatusConvite.PENDENTE
            ).count(),
            2,
        )

    def test_vinculo_duplicado_bloqueado(self):
        responsavel = Responsavel.objects.create(
            nome="Dup",
            email="dup@teste.com",
            senha=make_password("senha12345"),
        )
        ResponsavelAluno.objects.create(
            aluno=self.aluno,
            responsavel=responsavel,
            parentesco="MAE",
            status=StatusVinculo.ATIVO,
            data_aceitacao=timezone.now(),
        )
        self.auth_aluno()
        resp = self.client.post(
            "/api/responsaveis/convidar/",
            {
                "nome": "Dup",
                "email": "dup@teste.com",
                "parentesco": "MAE",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def _criar_vinculo_com_tarefa(self):
        responsavel = Responsavel.objects.create(
            nome="Resp",
            email="respview@teste.com",
            senha=make_password("senha12345"),
        )
        ResponsavelAluno.objects.create(
            aluno=self.aluno,
            responsavel=responsavel,
            parentesco="PAI",
            status=StatusVinculo.ATIVO,
            data_aceitacao=timezone.now(),
        )
        disc = Disciplina.objects.create(
            aluno=self.aluno, nome="Matemática", nivel_dificuldade=3
        )
        Tarefa.objects.create(
            disciplina=disc,
            descricao="Lista 1",
            status_tarefa="pendente",
            data_entrega=timezone.localdate(),
        )
        return responsavel

    def test_responsavel_visualiza_tarefas_autorizadas(self):
        responsavel = self._criar_vinculo_com_tarefa()
        tok = criar_token_acesso(
            tipo=TIPO_RESPONSAVEL,
            id_responsavel=responsavel.id_responsavel,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok}")
        resp = self.client.get(
            f"/api/responsaveis/alunos/{self.aluno.id_aluno}/tarefas/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["tarefas"]), 1)

    def test_responsavel_nao_ve_outro_aluno(self):
        responsavel = self._criar_vinculo_com_tarefa()
        outro = Aluno.objects.create(
            nome="Outro",
            email="outroaluno@teste.com",
            senha=make_password("senha12345"),
        )
        tok = criar_token_acesso(
            tipo=TIPO_RESPONSAVEL,
            id_responsavel=responsavel.id_responsavel,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok}")
        resp = self.client.get(f"/api/responsaveis/alunos/{outro.id_aluno}/tarefas/")
        self.assertEqual(resp.status_code, 403)

    def test_responsavel_nao_edita_tarefas(self):
        responsavel = self._criar_vinculo_com_tarefa()
        tarefa = Tarefa.objects.first()
        tok = criar_token_acesso(
            tipo=TIPO_RESPONSAVEL,
            id_responsavel=responsavel.id_responsavel,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok}")
        resp = self.client.patch(
            f"/api/tarefas/{tarefa.id_tarefa}/",
            {"descricao": "hack"},
            format="json",
        )
        self.assertIn(resp.status_code, (403, 401, 404))

    def test_responsavel_nao_acessa_cadernos(self):
        responsavel = self._criar_vinculo_com_tarefa()
        tok = criar_token_acesso(
            tipo=TIPO_RESPONSAVEL,
            id_responsavel=responsavel.id_responsavel,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok}")
        resp = self.client.get("/api/cadernos/")
        self.assertEqual(resp.status_code, 403)

    def test_responsavel_nao_acessa_assistente(self):
        responsavel = self._criar_vinculo_com_tarefa()
        tok = criar_token_acesso(
            tipo=TIPO_RESPONSAVEL,
            id_responsavel=responsavel.id_responsavel,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok}")
        resp = self.client.get("/api/assistente/historico/")
        self.assertEqual(resp.status_code, 403)

    def test_remocao_revoga_acesso(self):
        responsavel = self._criar_vinculo_com_tarefa()
        vinculo = ResponsavelAluno.objects.get(responsavel=responsavel)
        self.auth_aluno()
        rem = self.client.delete(f"/api/responsaveis/vinculos/{vinculo.id_vinculo}/")
        self.assertEqual(rem.status_code, 200)
        tok = criar_token_acesso(
            tipo=TIPO_RESPONSAVEL,
            id_responsavel=responsavel.id_responsavel,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok}")
        resp = self.client.get(
            f"/api/responsaveis/alunos/{self.aluno.id_aluno}/dashboard/"
        )
        self.assertEqual(resp.status_code, 403)

    def test_soft_delete_convite(self):
        self.auth_aluno()
        criar = self.client.post(
            "/api/responsaveis/convidar/",
            {
                "nome": "Cancel",
                "email": "cancel@teste.com",
                "parentesco": "OUTRO",
            },
            format="json",
        )
        cid = criar.data["convite"]["id"]
        cancel = self.client.delete(f"/api/responsaveis/convites/{cid}/")
        self.assertEqual(cancel.status_code, 200)
        convite = ConviteResponsavel.objects.get(pk=cid)
        self.assertEqual(convite.status, StatusConvite.CANCELADO)
        self.assertIsNotNone(convite.data_exclusao)

    @patch("apps.responsaveis.emails.send_mail", side_effect=Exception("smtp down"))
    def test_falha_email_tratada(self, _mock):
        self.auth_aluno()
        resp = self.client.post(
            "/api/responsaveis/convidar/",
            {
                "nome": "Fail",
                "email": "fail@teste.com",
                "parentesco": "MAE",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 502)
        self.assertTrue(
            ConviteResponsavel.objects.filter(
                email_convidado="fail@teste.com",
                status=StatusConvite.FALHA_ENVIO,
            ).exists()
        )

    def test_login_unificado_responsavel(self):
        Responsavel.objects.create(
            nome="Log",
            email="loginresp@teste.com",
            senha=make_password("senha12345"),
        )
        resp = self.client.post(
            "/api/alunos/login/",
            {"email": "loginresp@teste.com", "senha": "senha12345"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["tipo"], TIPO_RESPONSAVEL)
