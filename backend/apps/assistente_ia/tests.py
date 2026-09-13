from unittest.mock import patch

from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

from apps.alunos.models import Aluno
from apps.alunos.services.auth_service import criar_token_acesso
from apps.assistente_ia.models import ConversaIA
from apps.assistente_ia.services import LIMITE_PERGUNTAS_POR_HORA
from apps.sistema_estudos.models import LogAtividade


class AssistenteIAPITestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.aluno_a = Aluno.objects.create(
            nome="Aluno A",
            email="ia-a@test.com",
            senha=make_password("senha123"),
        )
        self.aluno_b = Aluno.objects.create(
            nome="Aluno B",
            email="ia-b@test.com",
            senha=make_password("senha123"),
        )
        self.auth_a = {"HTTP_AUTHORIZATION": f"Bearer {criar_token_acesso(self.aluno_a.pk)}"}
        self.auth_b = {"HTTP_AUTHORIZATION": f"Bearer {criar_token_acesso(self.aluno_b.pk)}"}

    @patch("apps.assistente_ia.services.gerar_resposta_gemini")
    def test_pergunta_valida_salva_e_retorna_resposta(self, mock_gemini):
        mock_gemini.return_value = "Resposta didática sobre normalização."

        res = self.client.post(
            "/api/assistente/perguntar/",
            {"pergunta": "Explique normalização de forma simples."},
            format="json",
            **self.auth_a,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["resposta"], "Resposta didática sobre normalização.")
        self.assertEqual(ConversaIA.objects.filter(aluno=self.aluno_a).count(), 1)
        log = LogAtividade.objects.filter(acao="CONSULTA_IA", aluno=self.aluno_a).first()
        self.assertIsNotNone(log)
        mock_gemini.assert_called_once()

    def test_nao_autenticado_nao_pergunta(self):
        res = self.client.post(
            "/api/assistente/perguntar/",
            {"pergunta": "Teste"},
            format="json",
        )
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_pergunta_vazia_retorna_erro(self):
        res = self.client.post(
            "/api/assistente/perguntar/",
            {"pergunta": "   "},
            format="json",
            **self.auth_a,
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("erro" in res.data or "erros" in res.data)

    def test_pergunta_grande_demais_retorna_erro(self):
        res = self.client.post(
            "/api/assistente/perguntar/",
            {"pergunta": "a" * 2001},
            format="json",
            **self.auth_a,
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.assistente_ia.services.gerar_resposta_gemini")
    def test_falha_gemini_nao_salva_conversa(self, mock_gemini):
        from apps.assistente_ia.services import GeminiIndisponivelError

        mock_gemini.side_effect = GeminiIndisponivelError("falha")

        res = self.client.post(
            "/api/assistente/perguntar/",
            {"pergunta": "Teste falha"},
            format="json",
            **self.auth_a,
        )
        self.assertEqual(res.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(ConversaIA.objects.count(), 0)
        self.assertNotIn("GEMINI", str(res.data).upper())

    @patch("apps.assistente_ia.services.gerar_resposta_gemini")
    def test_historico_isolado_entre_alunos(self, mock_gemini):
        mock_gemini.return_value = "Ok"
        self.client.post(
            "/api/assistente/perguntar/",
            {"pergunta": "Privado"},
            format="json",
            **self.auth_a,
        )
        res_b = self.client.get("/api/assistente/historico/", **self.auth_b)
        self.assertEqual(res_b.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_b.data), 0)

        res_a = self.client.get("/api/assistente/historico/", **self.auth_a)
        self.assertEqual(len(res_a.data), 1)

    @patch("apps.assistente_ia.services.gerar_resposta_gemini")
    def test_soft_delete_historico(self, mock_gemini):
        mock_gemini.return_value = "Resposta"
        post = self.client.post(
            "/api/assistente/perguntar/",
            {"pergunta": "Apagar depois"},
            format="json",
            **self.auth_a,
        )
        conversa_id = ConversaIA.objects.first().pk

        delete = self.client.delete(
            f"/api/assistente/historico/{conversa_id}/",
            **self.auth_a,
        )
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        conversa = ConversaIA.objects.get(pk=conversa_id)
        self.assertIsNotNone(conversa.data_exclusao)

        lista = self.client.get("/api/assistente/historico/", **self.auth_a)
        self.assertEqual(len(lista.data), 0)

    @patch("apps.assistente_ia.services.gerar_resposta_gemini")
    def test_limite_uso_por_hora(self, mock_gemini):
        mock_gemini.return_value = "Resposta"

        for i in range(LIMITE_PERGUNTAS_POR_HORA):
            res = self.client.post(
                "/api/assistente/perguntar/",
                {"pergunta": f"Pergunta {i}"},
                format="json",
                **self.auth_a,
            )
            self.assertEqual(res.status_code, status.HTTP_200_OK)

        res_limite = self.client.post(
            "/api/assistente/perguntar/",
            {"pergunta": "Ultrapassou limite"},
            format="json",
            **self.auth_a,
        )
        self.assertEqual(res_limite.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("limite", res_limite.data["erro"].lower())

    @patch("apps.assistente_ia.services.gerar_resposta_gemini")
    def test_aluno_b_nao_apaga_historico_de_aluno_a(self, mock_gemini):
        mock_gemini.return_value = "Resposta"
        self.client.post(
            "/api/assistente/perguntar/",
            {"pergunta": "Minha pergunta"},
            format="json",
            **self.auth_a,
        )
        conversa_id = ConversaIA.objects.first().pk
        res = self.client.delete(
            f"/api/assistente/historico/{conversa_id}/",
            **self.auth_b,
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.assistente_ia.services.gerar_resposta_gemini")
    def test_resposta_erro_nao_expoe_api_key(self, mock_gemini):
        from apps.assistente_ia.services import GeminiConfigError

        mock_gemini.side_effect = GeminiConfigError("key ausente")
        res = self.client.post(
            "/api/assistente/perguntar/",
            {"pergunta": "Teste"},
            format="json",
            **self.auth_a,
        )
        self.assertEqual(res.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        corpo = str(res.data).lower()
        self.assertNotIn("gemini_api_key", corpo)
        self.assertNotIn("key ausente", corpo)
