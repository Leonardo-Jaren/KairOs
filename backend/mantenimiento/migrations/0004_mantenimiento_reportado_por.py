from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def sincronizar_reportantes_existentes(apps, schema_editor):
    """Conserva el creador como reportante para los tickets ya registrados."""
    mantenimiento = apps.get_model('mantenimiento', 'Mantenimiento')
    mantenimiento.objects.filter(
        reportado_por__isnull=True,
        created_by__isnull=False,
    ).update(reportado_por_id=models.F('created_by_id'))


def limpiar_reportantes_sincronizados(apps, schema_editor):
    mantenimiento = apps.get_model('mantenimiento', 'Mantenimiento')
    mantenimiento.objects.filter(
        reportado_por_id=models.F('created_by_id'),
    ).update(reportado_por=None)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mantenimiento', '0003_mantenimiento_created_at_mantenimiento_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mantenimiento',
            name='reportado_por',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='mantenimientos_reportados',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Reportado por',
            ),
        ),
        migrations.RunPython(
            sincronizar_reportantes_existentes,
            limpiar_reportantes_sincronizados,
        ),
    ]
