from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('espacios', '0003_espaciousuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='espacio',
            name='activo',
            field=models.BooleanField(default=True, verbose_name='Espacio activo'),
        ),
    ]
