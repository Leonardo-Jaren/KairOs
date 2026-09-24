from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('incidencias', '0006_incidencia_operacion'),
        ('mantenimiento', '0004_mantenimiento_reportado_por'),
    ]

    operations = [
        migrations.AddField(
            model_name='mantenimiento',
            name='diagnostico',
            field=models.TextField(blank=True, default='', verbose_name='Diagnóstico'),
        ),
        migrations.AddField(
            model_name='mantenimiento',
            name='fecha_fin',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fin de atención'),
        ),
        migrations.AddField(
            model_name='mantenimiento',
            name='fecha_inicio',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Inicio de atención'),
        ),
        migrations.AddField(
            model_name='mantenimiento',
            name='incidencia_origen',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='mantenimientos',
                to='incidencias.incidencia',
                verbose_name='Incidencia de origen',
            ),
        ),
        migrations.AddField(
            model_name='mantenimiento',
            name='resultado_equipo',
            field=models.CharField(
                blank=True,
                choices=[
                    ('en_uso', 'En uso'),
                    ('en_mantenimiento', 'En mantenimiento'),
                    ('dañado', 'Dañado'),
                    ('de_baja', 'De baja'),
                ],
                max_length=20,
                null=True,
                verbose_name='Resultado del equipo',
            ),
        ),
        migrations.AddField(
            model_name='mantenimiento',
            name='trabajo_realizado',
            field=models.TextField(blank=True, default='', verbose_name='Trabajo realizado'),
        ),
        migrations.AddIndex(
            model_name='mantenimiento',
            index=models.Index(fields=['incidencia_origen'], name='idx_mant_incidencia'),
        ),
    ]
