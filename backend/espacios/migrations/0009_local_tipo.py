from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('espacios', '0008_local_edificio_local'),
    ]

    operations = [
        migrations.AddField(
            model_name='local',
            name='tipo',
            field=models.CharField(
                choices=[
                    ('campus', 'Campus'),
                    ('sede', 'Sede'),
                    ('anexo', 'Anexo'),
                    ('otro', 'Otro'),
                ],
                default='sede',
                max_length=20,
                verbose_name='Tipo de ubicación',
            ),
        ),
        migrations.AddIndex(
            model_name='local',
            index=models.Index(fields=['tipo'], name='idx_local_tipo'),
        ),
    ]
