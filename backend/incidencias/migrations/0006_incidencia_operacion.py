from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('equipos', '0002_componente_created_at_componente_created_by_and_more'),
        ('espacios', '0010_espaciousuario_ambito_and_scopes'),
        ('usuarios', '0004_permisopersonalizado_usuariosede_usuario_supervisor_and_more'),
        ('incidencias', '0005_alter_incidencia_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidencia',
            name='asignado_a',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='incidencias_asignadas',
                to='usuarios.perfiltecnico',
                verbose_name='Técnico asignado',
            ),
        ),
        migrations.AddField(
            model_name='incidencia',
            name='motivo_cierre',
            field=models.TextField(blank=True, default='', verbose_name='Motivo de cierre'),
        ),
        migrations.AddField(
            model_name='incidencia',
            name='prioridad',
            field=models.CharField(
                choices=[
                    ('baja', 'Baja'),
                    ('media', 'Media'),
                    ('alta', 'Alta'),
                    ('critica', 'Crítica'),
                ],
                default='media',
                max_length=20,
                verbose_name='Prioridad',
            ),
        ),
        migrations.AddField(
            model_name='incidencia',
            name='resolucion',
            field=models.TextField(blank=True, default='', verbose_name='Resolución'),
        ),
        migrations.AlterField(
            model_name='incidencia',
            name='estado',
            field=models.CharField(
                choices=[
                    ('pendiente', 'Pendiente'),
                    ('en_proceso', 'En Proceso'),
                    ('resuelto', 'Resuelto'),
                    ('cerrado', 'Cerrado'),
                    ('cancelado', 'Cancelado'),
                    ('duplicado', 'Duplicado'),
                ],
                default='pendiente',
                max_length=20,
                verbose_name='Estado',
            ),
        ),
        migrations.AlterField(
            model_name='incidencia',
            name='fecha_resolucion',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de resolución'),
        ),
        migrations.AddIndex(
            model_name='incidencia',
            index=models.Index(fields=['prioridad'], name='idx_incidencia_prioridad'),
        ),
        migrations.AddIndex(
            model_name='incidencia',
            index=models.Index(fields=['asignado_a'], name='idx_incidencia_asignado'),
        ),
    ]
