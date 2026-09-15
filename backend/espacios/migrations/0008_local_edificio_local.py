from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('espacios', '0007_edificio_configuracion_croquis'),
    ]

    operations = [
        migrations.CreateModel(
            name='Local',
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
                    'codigo',
                    models.CharField(
                        help_text='Identificador global del local, por ejemplo LOC-01.',
                        max_length=50,
                        unique=True,
                        verbose_name='Código del local',
                    ),
                ),
                (
                    'nombre',
                    models.CharField(max_length=100, verbose_name='Nombre del local'),
                ),
                (
                    'ciudad',
                    models.CharField(max_length=100, verbose_name='Ciudad del local'),
                ),
                (
                    'descripcion',
                    models.TextField(blank=True, default='', verbose_name='Descripción'),
                ),
                (
                    'activo',
                    models.BooleanField(default=True, verbose_name='Local activo'),
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
            ],
            options={
                'verbose_name': 'Local',
                'verbose_name_plural': 'Locales',
                'db_table': 'locales',
                'ordering': ['nombre', 'codigo'],
                'indexes': [
                    models.Index(fields=['codigo'], name='idx_local_codigo'),
                    models.Index(fields=['nombre'], name='idx_local_nombre'),
                    models.Index(fields=['ciudad'], name='idx_local_ciudad'),
                    models.Index(fields=['activo'], name='idx_local_activo'),
                ],
            },
        ),
        migrations.AddField(
            model_name='edificio',
            name='local',
            field=models.ForeignKey(
                blank=True,
                help_text='Sede física a la que pertenece el edificio.',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='edificios',
                to='espacios.local',
                verbose_name='Local',
            ),
        ),
    ]
