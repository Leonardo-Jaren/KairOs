import re
import unicodedata

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def _codigo_disponible(Edificio, nombre):
    """Genera un código estable y evita colisiones entre pabellones."""
    normalizado = unicodedata.normalize('NFKD', nombre)
    ascii_nombre = normalizado.encode('ascii', 'ignore').decode('ascii')
    base = re.sub(r'[^A-Z0-9]+', '-', ascii_nombre.upper()).strip('-')
    base = (base or 'EDIFICIO')[:50]
    codigo = base
    correlativo = 2
    while Edificio.objects.filter(codigo=codigo).exists():
        sufijo = f'-{correlativo}'
        codigo = f'{base[:50 - len(sufijo)]}{sufijo}'
        correlativo += 1
    return codigo


def agrupar_pabellones(apps, schema_editor):
    """Crea edificios a partir de los pabellones y vincula cada espacio."""
    Edificio = apps.get_model('espacios', 'Edificio')
    Espacio = apps.get_model('espacios', 'Espacio')
    edificios_por_nombre = {}

    espacios = Espacio.objects.exclude(pabellon='').order_by('id')
    for espacio in espacios.iterator():
        nombre = ' '.join(espacio.pabellon.split())
        if not nombre:
            continue
        clave = nombre.casefold()
        edificio = edificios_por_nombre.get(clave)
        if edificio is None:
            edificio = Edificio.objects.create(
                codigo=_codigo_disponible(Edificio, nombre),
                nombre=nombre,
                descripcion='Creado automáticamente desde los pabellones existentes.',
                activo=True,
            )
            edificios_por_nombre[clave] = edificio
        Espacio.objects.filter(pk=espacio.pk).update(edificio_id=edificio.pk)


def desagrupar_pabellones(apps, schema_editor):
    """Desvincula los espacios antes de retirar la estructura de edificios."""
    Edificio = apps.get_model('espacios', 'Edificio')
    Espacio = apps.get_model('espacios', 'Espacio')
    Espacio.objects.update(edificio_id=None)
    Edificio.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('espacios', '0005_espacio_configuracion_plano'),
    ]

    operations = [
        migrations.CreateModel(
            name='Edificio',
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
                        help_text='Ej: EDIF-01',
                        max_length=50,
                        unique=True,
                        verbose_name='Código del edificio',
                    ),
                ),
                (
                    'nombre',
                    models.CharField(
                        help_text='Ej: Edificio 1',
                        max_length=100,
                        verbose_name='Nombre del edificio',
                    ),
                ),
                (
                    'descripcion',
                    models.TextField(
                        blank=True,
                        default='',
                        verbose_name='Descripción',
                    ),
                ),
                (
                    'activo',
                    models.BooleanField(
                        default=True,
                        verbose_name='Edificio activo',
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
                'verbose_name': 'Edificio',
                'verbose_name_plural': 'Edificios',
                'db_table': 'edificios',
                'ordering': ['nombre', 'codigo'],
                'indexes': [
                    models.Index(fields=['codigo'], name='idx_edificio_codigo'),
                    models.Index(fields=['nombre'], name='idx_edificio_nombre'),
                    models.Index(fields=['activo'], name='idx_edificio_activo'),
                ],
            },
        ),
        migrations.AddField(
            model_name='espacio',
            name='edificio',
            field=models.ForeignKey(
                blank=True,
                help_text='Bloque físico al que pertenece el espacio.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='espacios',
                to='espacios.edificio',
                verbose_name='Edificio',
            ),
        ),
        migrations.RunPython(agrupar_pabellones, desagrupar_pabellones),
    ]
