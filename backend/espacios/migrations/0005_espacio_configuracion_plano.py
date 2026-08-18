from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('espacios', '0004_espacio_activo'),
    ]

    operations = [
        migrations.AddField(
            model_name='espacio',
            name='configuracion_plano',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Filas, columnas y posiciones de los equipos dentro del espacio.',
                verbose_name='Configuración del plano',
            ),
        ),
    ]
