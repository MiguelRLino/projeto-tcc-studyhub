# Generated manually

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("alunos", "__first__"),
        ("sistema_estudos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConfiguracaoTelegram",
            fields=[
                ("id_configuracao", models.AutoField(primary_key=True, serialize=False)),
                ("telegram_chat_id", models.BigIntegerField(blank=True, null=True)),
                ("telegram_username", models.CharField(blank=True, default="", max_length=100)),
                ("telegram_ativo", models.BooleanField(default=False)),
                ("notificar_24h", models.BooleanField(default=True)),
                ("notificar_2h", models.BooleanField(default=True)),
                ("data_conexao", models.DateTimeField(blank=True, null=True)),
                ("data_atualizacao", models.DateTimeField(auto_now=True)),
                ("data_exclusao", models.DateTimeField(blank=True, null=True)),
                (
                    "aluno",
                    models.OneToOneField(
                        db_column="aluno_id_aluno",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="configuracao_telegram",
                        to="alunos.aluno",
                    ),
                ),
            ],
            options={
                "verbose_name": "Configuração Telegram",
                "verbose_name_plural": "Configurações Telegram",
                "db_table": "configuracao_telegram",
            },
        ),
        migrations.CreateModel(
            name="CodigoConexaoTelegram",
            fields=[
                ("id_codigo", models.AutoField(primary_key=True, serialize=False)),
                ("codigo", models.CharField(db_index=True, max_length=10)),
                ("data_criacao", models.DateTimeField(auto_now_add=True)),
                ("data_expiracao", models.DateTimeField()),
                ("utilizado", models.BooleanField(default=False)),
                (
                    "aluno",
                    models.ForeignKey(
                        db_column="aluno_id_aluno",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="codigos_telegram",
                        to="alunos.aluno",
                    ),
                ),
            ],
            options={
                "verbose_name": "Código conexão Telegram",
                "verbose_name_plural": "Códigos conexão Telegram",
                "db_table": "codigo_conexao_telegram",
                "ordering": ["-data_criacao"],
            },
        ),
        migrations.CreateModel(
            name="NotificacaoTelegram",
            fields=[
                ("id_notificacao", models.AutoField(primary_key=True, serialize=False)),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("TAREFA_24H", "Tarefa 24h"),
                            ("TAREFA_2H", "Tarefa 2h"),
                        ],
                        max_length=20,
                    ),
                ),
                ("status_envio", models.CharField(default="enviado", max_length=20)),
                ("data_envio", models.DateTimeField(auto_now_add=True)),
                ("erro", models.CharField(blank=True, default="", max_length=255)),
                ("data_criacao", models.DateTimeField(auto_now_add=True)),
                (
                    "aluno",
                    models.ForeignKey(
                        db_column="aluno_id_aluno",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="notificacoes_telegram",
                        to="alunos.aluno",
                    ),
                ),
                (
                    "tarefa",
                    models.ForeignKey(
                        db_column="tarefa_id_tarefa",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="notificacoes_telegram",
                        to="sistema_estudos.tarefa",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notificação Telegram",
                "verbose_name_plural": "Notificações Telegram",
                "db_table": "notificacao_telegram",
            },
        ),
        migrations.AddConstraint(
            model_name="notificacaotelegram",
            constraint=models.UniqueConstraint(
                fields=("aluno", "tarefa", "tipo"),
                name="uniq_notificacao_telegram_tarefa_tipo",
            ),
        ),
    ]
