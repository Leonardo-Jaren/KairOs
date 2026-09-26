import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mantenimiento', '0005_mantenimiento_operacion'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='mantenimiento',
            name='prueba_realizada',
            field=models.BooleanField(
                default=False,
                verbose_name='Prueba de funcionamiento realizada',
            ),
        ),
        migrations.AddField(
            model_name='mantenimiento',
            name='observacion_prueba',
            field=models.TextField(
                blank=True,
                default='',
                verbose_name='Observación de la prueba',
            ),
        ),
        migrations.AddField(
            model_name='mantenimiento',
            name='verificado_por',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='mantenimientos_verificados',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Verificado por',
            ),
        ),
        migrations.AddField(
            model_name='mantenimiento',
            name='fecha_verificacion',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Fecha de verificación',
            ),
        ),
    ]
