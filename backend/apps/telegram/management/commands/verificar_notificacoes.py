from django.core.management.base import BaseCommand

from apps.telegram.notificacao_service import verificar_e_enviar_notificacoes


class Command(BaseCommand):
    help = (
        "Verifica tarefas próximas do vencimento e envia notificações Telegram. "
        "Use --loop para executar automaticamente em intervalos."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--loop",
            action="store_true",
            help="Executa continuamente até Ctrl+C.",
        )
        parser.add_argument(
            "--intervalo-minutos",
            type=int,
            default=15,
            help="Intervalo entre verificações quando --loop (padrão: 15).",
        )

    def _imprimir_resumo(self, stats):
        self.stdout.write(
            f"{stats['analisadas']} tarefas analisadas\n"
            f"{stats['enviadas']} notificações enviadas\n"
            f"{stats['ignoradas']} ignoradas\n"
            f"{stats['erros']} erros"
        )

    def handle(self, *args, **options):
        import time

        from django.utils import timezone

        loop = options["loop"]
        intervalo = max(1, options["intervalo_minutos"])

        if not loop:
            self._imprimir_resumo(verificar_e_enviar_notificacoes())
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Notificações automáticas ativas (a cada {intervalo} min). Ctrl+C para encerrar."
            )
        )
        try:
            while True:
                agora = timezone.localtime().strftime("%d/%m/%Y %H:%M:%S")
                self.stdout.write(f"\n[{agora}] Verificando tarefas…")
                stats = verificar_e_enviar_notificacoes()
                self._imprimir_resumo(stats)
                self.stdout.write(f"Próxima verificação em {intervalo} min…")
                time.sleep(intervalo * 60)
        except KeyboardInterrupt:
            self.stdout.write("\nVerificação automática encerrada.")
