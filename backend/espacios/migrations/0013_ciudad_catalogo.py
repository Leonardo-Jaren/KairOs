import unicodedata

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def normalizar_nombre(nombre):
    nombre_limpio = ' '.join(str(nombre or '').split())
    descompuesto = unicodedata.normalize('NFKD', nombre_limpio)
    sin_tildes = ''.join(
        caracter for caracter in descompuesto
        if not unicodedata.combining(caracter)
    )
    return sin_tildes.casefold()


def vincular_ciudades_existentes(apps, schema_editor):
    Ciudad = apps.get_model('espacios', 'Ciudad')
    Local = apps.get_model('espacios', 'Local')
    ciudades = {}

    for local in Local.objects.order_by('id').iterator():
        nombre = ' '.join(str(local.ciudad_legacy or '').split())
        clave = normalizar_nombre(nombre)
        if not clave:
            local.ciudad_id = None
            local.save(update_fields=['ciudad'])
            continue

        ciudad = ciudades.get(clave)
        if ciudad is None:
            ciudad = Ciudad.objects.create(
                nombre=nombre,
                nombre_normalizado=clave,
            )
            ciudades[clave] = ciudad
        local.ciudad_id = ciudad.id
        local.save(update_fields=['ciudad'])


def restaurar_ciudades_textuales(apps, schema_editor):
    Local = apps.get_model('espacios', 'Local')
    for local in Local.objects.select_related('ciudad').iterator():
        local.ciudad_legacy = local.ciudad.nombre if local.ciudad_id else ''
        local.save(update_fields=['ciudad_legacy'])


class Migration(migrations.Migration):

    dependencies = [
        ('espacios', '0012_allow_duplicate_space_codes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='local',
            name='idx_local_ciudad',
        ),
        migrations.CreateModel(
            name='Ciudad',
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
                    models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación'),
                ),
                (
                    'updated_at',
                    models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización'),
                ),
                (
                    'is_deleted',
                    models.BooleanField(default=False, verbose_name='Eliminado (Soft Delete)'),
                ),
                (
                    'nombre',
                    models.CharField(max_length=100, verbose_name='Nombre de la ciudad'),
                ),
                (
                    'nombre_normalizado',
                    models.CharField(
                        editable=False,
                        max_length=100,
                        unique=True,
                        verbose_name='Nombre normalizado',
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
                'verbose_name': 'Ciudad',
                'verbose_name_plural': 'Ciudades',
                'db_table': 'ciudades',
                'ordering': ['nombre'],
            },
        ),
        migrations.RenameField(
            model_name='local',
            old_name='ciudad',
            new_name='ciudad_legacy',
        ),
        migrations.AddField(
            model_name='local',
            name='ciudad',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='locales',
                to='espacios.ciudad',
                verbose_name='Ciudad del local',
            ),
        ),
        migrations.RunPython(vincular_ciudades_existentes, restaurar_ciudades_textuales),
        migrations.RemoveField(
            model_name='local',
            name='ciudad_legacy',
        ),
    ]
