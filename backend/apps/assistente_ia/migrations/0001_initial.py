# Generated manually for Assistente IA

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("alunos", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConversaIA",
            fields=[
                (
                    "id_conversa",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("pergunta", models.TextField()),
                ("resposta", models.TextField()),
                ("data_criacao", models.DateTimeField(auto_now_add=True)),
                ("data_exclusao", models.DateTimeField(blank=True, null=True)),
                (
                    "aluno",
                    models.ForeignKey(
                        db_column="aluno_id_aluno",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="conversas_ia",
                        to="alunos.aluno",
                    ),
                ),
            ],
            options={
                "verbose_name": "Conversa com IA",
                "verbose_name_plural": "Conversas com IA",
                "db_table": "conversa_ia",
                "ordering": ["-data_criacao"],
            },
        ),
    ]
