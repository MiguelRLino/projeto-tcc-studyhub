from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sistema_estudos", "0002_sessaoplanejada"),
    ]

    operations = [
        migrations.AddField(
            model_name="tarefa",
            name="hora_entrega",
            field=models.TimeField(blank=True, null=True),
        ),
    ]
