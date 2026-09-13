from django.contrib.auth.hashers import make_password
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.alunos.models import Aluno
from apps.alunos.services.auth_service import criar_token_acesso, decodificar_token
from apps.alunos.services.senha_validator import validar_senha_forte

SENHA_VALIDA = "Senha@123"


class SenhaValidatorTestCase(TestCase):
    def test_senha_valida_sem_erros(self):
        self.assertEqual(validar_senha_forte(SENHA_VALIDA), [])

    def test_senha_curta(self):
        erros = validar_senha_forte("Ab@1")
        self.assertTrue(any("8 caracteres" in e for e in erros))

    def test_senha_sem_maiuscula(self):
        erros = validar_senha_forte("senha@123")
        self.assertTrue(any("maiúscula" in e for e in erros))

    def test_senha_sem_numero(self):
        erros = validar_senha_forte("Senha@abc")
        self.assertTrue(any("número" in e for e in erros))

    def test_senha_sem_especial(self):
        erros = validar_senha_forte("Senha1234")
        self.assertTrue(any("especial" in e for e in erros))


class AuthServiceTestCase(TestCase):
    def test_criar_e_decodificar_token(self):
        aluno = Aluno.objects.create(
            nome="Token Test",
            email="token@test.com",
            senha=make_password(SENHA_VALIDA),
        )
        token = criar_token_acesso(aluno.pk)
        payload = decodificar_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["id_aluno"], aluno.pk)


class AlunoAuthAPITestCase(APITestCase):
    def setUp(self):
        self.aluno = Aluno.objects.create(
            nome="Usuario Auth",
            email="auth@test.com",
            senha=make_password(SENHA_VALIDA),
        )
        self.auth = {
            "HTTP_AUTHORIZATION": f"Bearer {criar_token_acesso(self.aluno.pk)}"
        }

    def test_login_sucesso(self):
        res = self.client.post(
            "/api/alunos/login/",
            {"email": "auth@test.com", "senha": SENHA_VALIDA},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertEqual(res.data["aluno"]["email"], "auth@test.com")

    def test_login_senha_incorreta(self):
        res = self.client.post(
            "/api/alunos/login/",
            {"email": "auth@test.com", "senha": "Errada@999"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("erro", res.data)

    def test_login_email_inexistente(self):
        res = self.client.post(
            "/api/alunos/login/",
            {"email": "naoexiste@test.com", "senha": SENHA_VALIDA},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_autentica_rota_protegida(self):
        res = self.client.get("/api/alunos/me/", **self.auth)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], "auth@test.com")

    def test_cadastro_senha_valida(self):
        res = self.client.post(
            "/api/alunos/cadastro/",
            {
                "nome": "Novo Aluno",
                "email": "novo@test.com",
                "senha": SENHA_VALIDA,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", res.data)

    def test_cadastro_rejeita_senha_curta(self):
        res = self.client.post(
            "/api/alunos/cadastro/",
            {"nome": "A", "email": "curta@test.com", "senha": "Ab@1"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cadastro_rejeita_sem_maiuscula(self):
        res = self.client.post(
            "/api/alunos/cadastro/",
            {"nome": "A", "email": "semmaius@test.com", "senha": "senha@123"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cadastro_rejeita_sem_numero(self):
        res = self.client.post(
            "/api/alunos/cadastro/",
            {"nome": "A", "email": "semnum@test.com", "senha": "Senha@abc"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cadastro_rejeita_sem_especial(self):
        res = self.client.post(
            "/api/alunos/cadastro/",
            {"nome": "A", "email": "semesp@test.com", "senha": "Senha1234"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_alterar_senha_rejeita_nova_senha_fraca(self):
        res = self.client.post(
            "/api/alunos/me/senha/",
            {"senha_atual": SENHA_VALIDA, "senha_nova": "fraca123"},
            format="json",
            **self.auth,
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_alterar_senha_sucesso(self):
        nova = "NovaSenha@99"
        res = self.client.post(
            "/api/alunos/me/senha/",
            {"senha_atual": SENHA_VALIDA, "senha_nova": nova},
            format="json",
            **self.auth,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.aluno.refresh_from_db()
        login = self.client.post(
            "/api/alunos/login/",
            {"email": "auth@test.com", "senha": nova},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
