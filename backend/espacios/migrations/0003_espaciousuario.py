import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('espacios', '0002_espacio_created_at_espacio_created_by_and_more'),
        ('usuarios', '0003_usuario_apellido_y_rol_docente'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EspacioUsuario',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='Fecha de creación',
                    ),
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name='Fecha de actualización',
                    ),
                ),
                (
                    'is_deleted',
                    models.BooleanField(
                        default=False,
                        verbose_name='Eliminado (Soft Delete)',
                    ),
                ),
                (
                    'tipo_responsabilidad',
                    models.CharField(
                        choices=[
                            ('responsable', 'Responsable'),
                            ('tecnico', 'Soporte técnico'),
                            ('docente', 'Docente asignado'),
                        ],
                        default='responsable',
                        max_length=20,
                        verbose_name='Tipo de responsabilidad',
                    ),
                ),
                (
                    'activo',
                    models.BooleanField(
                        default=True,
                        verbose_name='Asignación activa',
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='+',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Creado por',
                    ),
                ),
                (
                    'espacio',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='asignaciones_usuario',
                        to='espacios.espacio',
                        verbose_name='Espacio',
                    ),
                ),
                (
                    'updated_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='+',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Actualizado por',
                    ),
                ),
                (
                    'usuario',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='asignaciones_espacio',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Usuario',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Asignación de usuario a espacio',
                'verbose_name_plural': 'Asignaciones de usuarios a espacios',
                'db_table': 'espacios_usuarios',
                'ordering': ['espacio__codigo_espacio', 'usuario__nombre'],
                'indexes': [
                    models.Index(
                        fields=['espacio', 'activo'],
                        name='idx_asig_esp_activa',
                    ),
                    models.Index(
                        fields=['usuario', 'activo'],
                        name='idx_asig_usr_activa',
                    ),
                ],
                'constraints': [
                    models.UniqueConstraint(
                        fields=('espacio', 'usuario'),
                        name='uniq_espacio_usuario',
                    ),
                ],
            },
        ),
    ]
