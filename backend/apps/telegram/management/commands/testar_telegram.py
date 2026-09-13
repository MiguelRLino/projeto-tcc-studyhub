from django.core.management.base import BaseCommand, CommandError

from apps.alunos.models import Aluno
from apps.telegram.notificacao_service import enviar_mensagem_teste
from apps.telegram.services import TelegramServiceError


class Command(BaseCommand):
    help = "Envia mensagem de teste pelo Telegram para um aluno."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=int,
            required=True,
            help="ID do aluno (id_aluno)",
        )

    def handle(self, *args, **options):
        aluno_id = options["user"]
        try:
            aluno = Aluno.objects.get(pk=aluno_id)
        except Aluno.DoesNotExist as exc:
            raise CommandError(f"Aluno {aluno_id} não encontrado.") from exc

        try:
            enviar_mensagem_teste(aluno)
        except TelegramServiceError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(f"Mensagem de teste enviada para {aluno.nome}."))
