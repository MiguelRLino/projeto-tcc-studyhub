from django.core.management.base import BaseCommand

from apps.telegram.conexao_service import processar_mensagem_bot
from apps.telegram.services import TelegramService, TelegramServiceError


class Command(BaseCommand):
    help = "Aguarda mensagens do bot Telegram (getUpdates) e processa /start e /conectar."

    def handle(self, *args, **options):
        self.stdout.write("Bot Telegram StudyHub iniciado. Ctrl+C para encerrar.")
        offset = None
        try:
            while True:
                try:
                    updates = TelegramService.obter_updates(offset=offset, timeout=30)
                except TelegramServiceError as exc:
                    self.stderr.write(f"Erro: {exc}")
                    continue

                for update in updates:
                    offset = update.get("update_id", 0) + 1
                    message = update.get("message") or {}
                    texto = message.get("text") or ""
                    chat = message.get("chat") or {}
                    chat_id = chat.get("id")
                    username = (message.get("from") or {}).get("username") or ""

                    if not chat_id or not texto:
                        continue

                    resposta = processar_mensagem_bot(texto, chat_id, username)
                    if resposta:
                        try:
                            TelegramService.enviar_mensagem(chat_id, resposta)
                        except TelegramServiceError as exc:
                            self.stderr.write(f"Falha ao responder chat {chat_id}: {exc}")
        except KeyboardInterrupt:
            self.stdout.write("\nBot encerrado.")
