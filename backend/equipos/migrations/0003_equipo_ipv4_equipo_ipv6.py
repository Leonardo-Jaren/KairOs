from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipos', '0002_componente_created_at_componente_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipo',
            name='ipv4',
            field=models.GenericIPAddressField(
                blank=True,
                default='',
                null=True,
                protocol='IPv4',
                verbose_name='Dirección IPv4',
            ),
        ),
        migrations.AddField(
            model_name='equipo',
            name='ipv6',
            field=models.GenericIPAddressField(
                blank=True,
                default='',
                null=True,
                protocol='IPv6',
                verbose_name='Dirección IPv6',
            ),
        ),
    ]
