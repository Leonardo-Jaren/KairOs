from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('espacios', '0006_edificio_espacio_edificio'),
    ]

    operations = [
        migrations.AddField(
            model_name='edificio',
            name='configuracion_croquis',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Dimensiones, ambientes y pasillos dibujados en cada piso.',
                verbose_name='Configuración de croquis por piso',
            ),
        ),
    ]
