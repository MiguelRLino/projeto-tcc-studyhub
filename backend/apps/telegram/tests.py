from datetime import datetime, time, timedelta
from unittest.mock import patch

from django.contrib.auth.hashers import make_password
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.alunos.models import Aluno
from apps.alunos.services.auth_service import criar_token_acesso
from apps.sistema_estudos.models import Disciplina, LogAtividade, Tarefa
from apps.telegram.conexao_service import (
    CODIGO_TTL_MINUTOS,
    conectar_por_codigo,
    desconectar_telegram,
    gerar_codigo_conexao,
    obter_ou_criar_config,
    processar_mensagem_bot,
)
from apps.telegram.models import CodigoConexaoTelegram, ConfiguracaoTelegram, NotificacaoTelegram
from apps.telegram.notificacao_service import verificar_e_enviar_notificacoes
from apps.telegram.services import TelegramService, TelegramServiceError


@override_settings(
    TELEGRAM_BOT_TOKEN="123456:TEST_TOKEN_SECRET",
    TELEGRAM_BOT_USERNAME="StudyHubBot",
)
class TelegramTestCase(APITestCase):
    def setUp(self):
        self.aluno_a = Aluno.objects.create(
            nome="Aluno A",
            email="tg-a@test.com",
            senha=make_password("senha123"),
        )
        self.aluno_b = Aluno.objects.create(
            nome="Aluno B",
            email="tg-b@test.com",
            senha=make_password("senha123"),
        )
        self.auth_a = {"HTTP_AUTHORIZATION": f"Bearer {criar_token_acesso(self.aluno_a.pk)}"}
        self.auth_b = {"HTTP_AUTHORIZATION": f"Bearer {criar_token_acesso(self.aluno_b.pk)}"}
        self.disc_a = Disciplina.objects.create(aluno=self.aluno_a, nome="Banco de Dados")
        self.disc_b = Disciplina.objects.create(aluno=self.aluno_b, nome="Redes")

    def _conectar_aluno(self, aluno, chat_id=999001):
        registro = gerar_codigo_conexao(aluno)
        ok, _ = conectar_por_codigo(registro.codigo, chat_id, "aluno_teste")
        self.assertTrue(ok)
        return obter_ou_criar_config(aluno)

    def _criar_tarefa(
        self,
        aluno=None,
        descricao="Trabalho de BD",
        data_entrega=None,
        hora_entrega=None,
        status_tarefa="pendente",
        excluida=False,
    ):
        aluno = aluno or self.aluno_a
        disc = self.disc_a if aluno == self.aluno_a else self.disc_b
        tarefa = Tarefa.objects.create(
            disciplina=disc,
            descricao=descricao,
            data_entrega=data_entrega or timezone.localdate(),
            hora_entrega=hora_entrega,
            status_tarefa=status_tarefa,
        )
        if excluida:
            tarefa.data_exclusao = timezone.now()
            tarefa.save(update_fields=["data_exclusao"])
        return tarefa

    def test_gerar_codigo_exige_autenticacao(self):
        res = self.client.post("/api/telegram/gerar-codigo/")
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_codigo_possui_expiracao(self):
        registro = gerar_codigo_conexao(self.aluno_a)
        delta = registro.data_expiracao - registro.data_criacao
        self.assertGreaterEqual(delta, timedelta(minutes=CODIGO_TTL_MINUTOS - 1))
        self.assertLessEqual(delta, timedelta(minutes=CODIGO_TTL_MINUTOS + 1))

    def test_codigo_so_pode_ser_usado_uma_vez(self):
        registro = gerar_codigo_conexao(self.aluno_a)
        ok1, _ = conectar_por_codigo(registro.codigo, 111, "user1")
        ok2, msg2 = conectar_por_codigo(registro.codigo, 222, "user2")
        self.assertTrue(ok1)
        self.assertFalse(ok2)
        self.assertIn("inválido", msg2.lower())

    def test_conectar_associa_chat_id_corretamente(self):
        registro = gerar_codigo_conexao(self.aluno_a)
        ok, msg = conectar_por_codigo(registro.codigo, 555777, "meu_user")
        self.assertTrue(ok)
        config = ConfiguracaoTelegram.objects.get(aluno=self.aluno_a)
        self.assertEqual(config.telegram_chat_id, 555777)
        self.assertEqual(config.telegram_username, "meu_user")
        self.assertTrue(config.telegram_ativo)
        self.assertIn("sucesso", msg.lower())

    def test_codigo_invalido_e_recusado(self):
        ok, msg = conectar_por_codigo("XXXXXX", 123, "")
        self.assertFalse(ok)
        self.assertIn("inválido", msg.lower())

    def test_aluno_nao_altera_config_de_outro(self):
        self._conectar_aluno(self.aluno_a, chat_id=1001)
        self._conectar_aluno(self.aluno_b, chat_id=1002)

        res = self.client.patch(
            "/api/telegram/configuracao/",
            {"notificar_24h": False},
            format="json",
            **self.auth_a,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        config_b = ConfiguracaoTelegram.objects.get(aluno=self.aluno_b)
        self.assertTrue(config_b.notificar_24h)

    def test_desconectar_funciona(self):
        self._conectar_aluno(self.aluno_a)
        res = self.client.delete("/api/telegram/desconectar/", **self.auth_a)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        config = ConfiguracaoTelegram.objects.get(aluno=self.aluno_a)
        self.assertFalse(config.telegram_ativo)
        self.assertIsNone(config.telegram_chat_id)

    def test_bot_token_nunca_aparece_na_resposta(self):
        self._conectar_aluno(self.aluno_a)
        res = self.client.get("/api/telegram/configuracao/", **self.auth_a)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        texto = str(res.data).lower()
        self.assertNotIn("test_token_secret", texto)
        self.assertNotIn("telegram_chat_id", texto)
        self.assertNotIn("123456:", texto)

    def test_gerar_codigo_via_api(self):
        res = self.client.post("/api/telegram/gerar-codigo/", **self.auth_a)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(res.data["codigo"]), 6)
        self.assertEqual(res.data["expira_em_minutos"], CODIGO_TTL_MINUTOS)

    def test_start_responde_instrucoes(self):
        msg = processar_mensagem_bot("/start", 1, "")
        self.assertIn("StudyHub", msg)
        self.assertIn("Perfil", msg)

    def test_conectar_via_bot(self):
        registro = gerar_codigo_conexao(self.aluno_a)
        msg = processar_mensagem_bot(f"/conectar {registro.codigo}", 888, "bot_user")
        self.assertIn("sucesso", msg.lower())
        config = ConfiguracaoTelegram.objects.get(aluno=self.aluno_a)
        self.assertEqual(config.telegram_chat_id, 888)

    def _agora_janela_24h(self, data_entrega, hora_entrega=None):
        hora = hora_entrega or time(14, 0)
        tz = timezone.get_current_timezone()
        entrega = timezone.make_aware(datetime.combine(data_entrega, hora), tz)
        return entrega - timedelta(hours=24)

    @patch("apps.telegram.notificacao_service.TelegramService.enviar_mensagem")
    def test_notificacao_24h_e_enviada(self, mock_enviar):
        mock_enviar.return_value = {"ok": True}
        self._conectar_aluno(self.aluno_a)
        amanha = timezone.localdate() + timedelta(days=1)
        self._criar_tarefa(data_entrega=amanha, hora_entrega=time(14, 0))
        agora = self._agora_janela_24h(amanha, time(14, 0))
        stats = verificar_e_enviar_notificacoes(agora)
        self.assertGreaterEqual(stats["enviadas"], 1)
        mock_enviar.assert_called()
        notif = NotificacaoTelegram.objects.filter(
            aluno=self.aluno_a, tipo=NotificacaoTelegram.TIPO_TAREFA_24H
        ).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.status_envio, NotificacaoTelegram.STATUS_ENVIADO)

    @patch("apps.telegram.notificacao_service.TelegramService.enviar_mensagem")
    def test_notificacao_2h_e_enviada(self, mock_enviar):
        mock_enviar.return_value = {"ok": True}
        self._conectar_aluno(self.aluno_a)
        hoje = timezone.localdate()
        hora_entrega = (timezone.localtime() + timedelta(hours=2)).time()
        self._criar_tarefa(data_entrega=hoje, hora_entrega=hora_entrega)
        agora = timezone.localtime()
        stats = verificar_e_enviar_notificacoes(agora)
        self.assertGreaterEqual(stats["enviadas"], 1)
        mock_enviar.assert_called()
        self.assertTrue(
            NotificacaoTelegram.objects.filter(
                tipo=NotificacaoTelegram.TIPO_TAREFA_2H
            ).exists()
        )

    @patch("apps.telegram.notificacao_service.TelegramService.enviar_mensagem")
    def test_tarefa_concluida_nao_gera_aviso(self, mock_enviar):
        mock_enviar.return_value = {"ok": True}
        self._conectar_aluno(self.aluno_a)
        amanha = timezone.localdate() + timedelta(days=1)
        self._criar_tarefa(data_entrega=amanha, status_tarefa="concluida")
        agora = timezone.make_aware(datetime.combine(amanha - timedelta(days=1), time(12, 0)))
        stats = verificar_e_enviar_notificacoes(agora)
        self.assertEqual(stats["enviadas"], 0)
        mock_enviar.assert_not_called()

    @patch("apps.telegram.notificacao_service.TelegramService.enviar_mensagem")
    def test_tarefa_excluida_nao_gera_aviso(self, mock_enviar):
        mock_enviar.return_value = {"ok": True}
        self._conectar_aluno(self.aluno_a)
        amanha = timezone.localdate() + timedelta(days=1)
        self._criar_tarefa(data_entrega=amanha, excluida=True)
        agora = timezone.make_aware(datetime.combine(amanha - timedelta(days=1), time(12, 0)))
        stats = verificar_e_enviar_notificacoes(agora)
        self.assertEqual(stats["enviadas"], 0)
        mock_enviar.assert_not_called()

    @patch("apps.telegram.notificacao_service.TelegramService.enviar_mensagem")
    def test_telegram_desativado_nao_recebe(self, mock_enviar):
        mock_enviar.return_value = {"ok": True}
        config = self._conectar_aluno(self.aluno_a)
        config.telegram_ativo = False
        config.save(update_fields=["telegram_ativo"])
        amanha = timezone.localdate() + timedelta(days=1)
        self._criar_tarefa(data_entrega=amanha)
        agora = timezone.make_aware(datetime.combine(amanha - timedelta(days=1), time(12, 0)))
        stats = verificar_e_enviar_notificacoes(agora)
        self.assertEqual(stats["enviadas"], 0)
        mock_enviar.assert_not_called()

    @patch("apps.telegram.notificacao_service.TelegramService.enviar_mensagem")
    def test_config_24h_desativada_nao_envia_24h(self, mock_enviar):
        mock_enviar.return_value = {"ok": True}
        config = self._conectar_aluno(self.aluno_a)
        config.notificar_24h = False
        config.save(update_fields=["notificar_24h"])
        amanha = timezone.localdate() + timedelta(days=1)
        self._criar_tarefa(data_entrega=amanha, hora_entrega=time(14, 0))
        agora = self._agora_janela_24h(amanha, time(14, 0))
        stats = verificar_e_enviar_notificacoes(agora)
        self.assertEqual(stats["enviadas"], 0)
        mock_enviar.assert_not_called()

    @patch("apps.telegram.notificacao_service.TelegramService.enviar_mensagem")
    def test_config_2h_desativada_nao_envia_2h(self, mock_enviar):
        mock_enviar.return_value = {"ok": True}
        config = self._conectar_aluno(self.aluno_a)
        config.notificar_2h = False
        config.save(update_fields=["notificar_2h"])
        hoje = timezone.localdate()
        hora_entrega = (timezone.localtime() + timedelta(hours=2)).time()
        self._criar_tarefa(data_entrega=hoje, hora_entrega=hora_entrega)
        stats = verificar_e_enviar_notificacoes(timezone.localtime())
        self.assertEqual(stats["enviadas"], 0)
        mock_enviar.assert_not_called()

    @patch("apps.telegram.notificacao_service.TelegramService.enviar_mensagem")
    def test_nao_envia_notificacao_duplicada(self, mock_enviar):
        mock_enviar.return_value = {"ok": True}
        self._conectar_aluno(self.aluno_a)
        amanha = timezone.localdate() + timedelta(days=1)
        self._criar_tarefa(data_entrega=amanha, hora_entrega=time(14, 0))
        agora = self._agora_janela_24h(amanha, time(14, 0))
        stats1 = verificar_e_enviar_notificacoes(agora)
        stats2 = verificar_e_enviar_notificacoes(agora)
        self.assertGreaterEqual(stats1["enviadas"], 1)
        self.assertEqual(stats2["enviadas"], 0)
        self.assertEqual(mock_enviar.call_count, 1)

    @patch("apps.telegram.notificacao_service.TelegramService.enviar_mensagem")
    def test_erro_api_e_tratado(self, mock_enviar):
        mock_enviar.side_effect = TelegramServiceError("chat not found")
        self._conectar_aluno(self.aluno_a)
        amanha = timezone.localdate() + timedelta(days=1)
        self._criar_tarefa(data_entrega=amanha, hora_entrega=time(14, 0))
        agora = self._agora_janela_24h(amanha, time(14, 0))
        stats = verificar_e_enviar_notificacoes(agora)
        self.assertGreaterEqual(stats["erros"], 1)
        notif = NotificacaoTelegram.objects.filter(
            aluno=self.aluno_a, tipo=NotificacaoTelegram.TIPO_TAREFA_24H
        ).first()
        self.assertEqual(notif.status_envio, NotificacaoTelegram.STATUS_ERRO)
        log = LogAtividade.objects.filter(
            aluno=self.aluno_a, acao="ERRO_NOTIFICACAO_TELEGRAM"
        ).first()
        self.assertIsNotNone(log)

    def test_codigo_expirado_e_recusado(self):
        registro = gerar_codigo_conexao(self.aluno_a)
        CodigoConexaoTelegram.objects.filter(pk=registro.pk).update(
            data_expiracao=timezone.now() - timedelta(minutes=1)
        )
        ok, msg = conectar_por_codigo(registro.codigo, 123, "")
        self.assertFalse(ok)
        self.assertIn("inválido", msg.lower())

    @patch("apps.telegram.services.requests.post")
    def test_servico_nao_expoe_token_em_erro(self, mock_post):
        mock_post.return_value.json.return_value = {
            "ok": False,
            "description": "Unauthorized",
        }
        mock_post.return_value.status_code = 401
        with self.assertRaises(TelegramServiceError) as ctx:
            TelegramService.enviar_mensagem(1, "teste")
        self.assertNotIn("TEST_TOKEN", str(ctx.exception))
