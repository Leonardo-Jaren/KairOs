from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('espacios', '0011_alter_espaciousuario_options_and_more'),
        ('usuarios', '0004_permisopersonalizado_usuariosede_usuario_supervisor_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='sedes',
            field=models.ManyToManyField(
                blank=True,
                related_name='usuarios',
                through='usuarios.UsuarioSede',
                through_fields=('usuario', 'local'),
                to='espacios.local',
                verbose_name='Sedes asignadas',
            ),
        ),
    ]
