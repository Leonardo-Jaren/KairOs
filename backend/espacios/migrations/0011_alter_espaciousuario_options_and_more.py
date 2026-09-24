import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('espacios', '0010_espaciousuario_ambito_and_scopes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='espaciousuario',
            options={
                'ordering': ['espacio__codigo_espacio', 'usuario__nombre'],
                'verbose_name': 'Asignación de usuario a ámbito territorial',
                'verbose_name_plural': 'Asignaciones de usuarios a ámbitos territoriales',
            },
        ),
        migrations.AlterField(
            model_name='espaciousuario',
            name='ambito',
            field=models.CharField(
                choices=[
                    ('sede', 'Sede'),
                    ('edificio', 'Pabellón/Edificio'),
                    ('piso', 'Piso'),
                    ('espacio', 'Espacio individual'),
                ],
                db_index=True,
                default='espacio',
                help_text='Granularidad física de la asignación (sede, edificio, piso, espacio).',
                max_length=20,
                verbose_name='Nivel de ámbito territorial',
            ),
        ),
        migrations.AlterField(
            model_name='espaciousuario',
            name='edificio',
            field=models.ForeignKey(
                blank=True,
                help_text='Referencia al edificio o pabellón. Obligatorio si el ámbito es edificio o piso.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='asignaciones_edificio',
                to='espacios.edificio',
                verbose_name='Edificio / Pabellón',
            ),
        ),
        migrations.AlterField(
            model_name='espaciousuario',
            name='espacio',
            field=models.ForeignKey(
                blank=True,
                help_text='Referencia al espacio físico específico. Obligatorio si el ámbito es espacio.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='asignaciones_usuario',
                to='espacios.espacio',
                verbose_name='Espacio individual',
            ),
        ),
        migrations.AlterField(
            model_name='espaciousuario',
            name='local',
            field=models.ForeignKey(
                blank=True,
                help_text='Referencia a la sede física. Obligatorio si el ámbito es sede.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='asignaciones_sede',
                to='espacios.local',
                verbose_name='Local / Sede',
            ),
        ),
        migrations.AlterField(
            model_name='espaciousuario',
            name='piso',
            field=models.CharField(
                blank=True,
                help_text='Identificador del piso (ej. "1", "2"). Obligatorio si el ámbito es piso.',
                max_length=20,
                null=True,
                verbose_name='Piso',
            ),
        ),
        migrations.AlterField(
            model_name='espaciousuario',
            name='usuario',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='asignaciones_espacio',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Usuario asignado',
            ),
        ),
    ]
