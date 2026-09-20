from django.core.management.base import BaseCommand

from usuarios.models import Usuario


class Command(BaseCommand):
    """Crea o actualiza un usuario docente para pruebas locales."""

    help = 'Crea (o reinicia la contrasena de) un usuario docente de pruebas.'

    def add_arguments(self, parser):
        parser.add_argument('--correo', default='docente@kairos.test', help='Correo de acceso del docente.')
        parser.add_argument('--password', default='Admin123!', help='Contrasena de acceso del docente.')
        parser.add_argument('--username', default='docente', help='Nombre de usuario.')
        parser.add_argument('--nombre', default='Ana', help='Nombre de pila.')
        parser.add_argument('--apellido', default='Torres', help='Apellido.')

    def handle(self, *args, **options):
        correo = options['correo'].strip().lower()
        password = options['password']

        usuario, creado = Usuario.objects.get_or_create(
            correo=correo,
            defaults={
                'username': options['username'],
                'nombre': options['nombre'],
                'apellido': options['apellido'],
            },
        )

        usuario.username = options['username']
        usuario.nombre = options['nombre']
        usuario.apellido = options['apellido']
        usuario.rol = 'docente'
        usuario.is_staff = False
        usuario.is_superuser = False
        usuario.is_active = True
        usuario.set_password(password)
        usuario.save()

        # Limpiar permisos personalizados previos para heredar la plantilla base del rol
        usuario.permisos_personalizados.all().delete()

        accion = 'creado' if creado else 'actualizado'
        self.stdout.write(self.style.SUCCESS(
            f'Usuario docente {accion} correctamente.\n'
            f'  Correo:      {correo}\n'
            f'  Contrasena:  {password}\n'
            f'  Nombre:      {usuario.nombre} {usuario.apellido}\n'
            f'  Rol:         {usuario.rol}'
        ))
