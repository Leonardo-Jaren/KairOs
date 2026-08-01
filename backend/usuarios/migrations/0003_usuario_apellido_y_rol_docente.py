from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_alter_usuario_options_perfiltecnico_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='dni',
            field=models.CharField(
                blank=True,
                max_length=8,
                null=True,
                unique=True,
                verbose_name='DNI',
            ),
        ),
        migrations.AddField(
            model_name='usuario',
            name='apellido',
            field=models.CharField(
                default='',
                max_length=255,
                verbose_name='Apellido completo',
            ),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.CharField(
                choices=[
                    ('usuario', 'Usuario'),
                    ('admin', 'Administrador'),
                    ('tecnico', 'Técnico'),
                    ('docente', 'Docente'),
                ],
                default='usuario',
                max_length=20,
                verbose_name='Rol',
            ),
        ),
    ]
