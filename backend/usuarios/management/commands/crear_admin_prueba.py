from django.core.management.base import BaseCommand

from usuarios.models import Usuario


class Command(BaseCommand):
    """Crea o actualiza un usuario administrador para pruebas locales."""

    help = 'Crea (o reinicia la contrasena de) un usuario administrador de pruebas.'

    def add_arguments(self, parser):
        parser.add_argument('--correo', default='admin@kairos.test', help='Correo de acceso del administrador.')
        parser.add_argument('--password', default='Admin123!', help='Contrasena de acceso del administrador.')
        parser.add_argument('--username', default='admin', help='Nombre de usuario.')
        parser.add_argument('--nombre', default='Administrador', help='Nombre de pila.')
        parser.add_argument('--apellido', default='KairOs', help='Apellido.')

    def handle(self, *args, **options):
        correo = options['correo'].strip().lower()
        password = options['password']

        usuario, creado = Usuario.objects.get_or_create(
            correo=correo,
            defaults={'username': options['username'], 'nombre': options['nombre']},
        )

        usuario.username = options['username']
        usuario.nombre = options['nombre']
        usuario.apellido = options['apellido']
        usuario.rol = 'admin'
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.is_active = True
        usuario.set_password(password)
        usuario.save()

        accion = 'creado' if creado else 'actualizado'
        self.stdout.write(self.style.SUCCESS(
            f'Usuario administrador {accion} correctamente.\n'
            f'  Correo:      {correo}\n'
            f'  Contrasena:  {password}\n'
            f'  Panel admin: /admin/ (usa el mismo correo y contrasena)'
        ))
