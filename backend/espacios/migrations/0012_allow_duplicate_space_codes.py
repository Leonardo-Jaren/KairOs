from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('espacios', '0011_alter_espaciousuario_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='espacio',
            name='codigo_espacio',
            field=models.CharField(
                help_text='Ej: LAB-203',
                max_length=50,
                verbose_name='Código del espacio',
            ),
        ),
    ]
