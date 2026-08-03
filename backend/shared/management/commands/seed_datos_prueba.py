import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from equipos.models import Equipo
from espacios.models import Espacio
from mantenimiento.models import Mantenimiento, TecnicoMantenimiento
from usuarios.models import PerfilTecnico, Usuario

PABELLONES = ['Pabellon 1', 'Pabellon 2', 'Pabellon 3', 'Pabellon 4']
TIPOS_ESPACIO = ['laboratorio', 'aula', 'sala_computo']
MARCAS = ['HP', 'Dell', 'Lenovo', 'Acer', 'Asus', 'Epson', 'Samsung']
MODELOS_POR_TIPO = {
    'desktop': ['OptiPlex 3080', 'ProDesk 400 G7', 'ThinkCentre M70'],
    'laptop': ['Latitude 5420', 'Aspire 5 A515', 'ThinkPad E14'],
    'monitor': ['E-Series 22"', 'V-Series 24"', 'ProDisplay 23.8"'],
    'impresora': ['LaserJet Pro M404', 'EcoTank L3250', 'WorkForce WF-2830'],
    'proyector': ['PowerLite X39', 'InFocus IN2124', 'ViewSonic PA503X'],
}
NOMBRES = [
    'Juan', 'Maria', 'Carlos', 'Ana', 'Luis', 'Claudia', 'Pedro', 'Eduardo',
    'Rosa', 'Jorge', 'Fiorella', 'Diego', 'Andrea', 'Kevin', 'Milagros',
]
APELLIDOS = [
    'Perez', 'Lopez', 'Ruiz', 'Garcia', 'Torres', 'Silva', 'Mendoza',
    'Morales', 'Ramos', 'Castillo', 'Vargas', 'Salazar', 'Chavez',
]
AREAS = ['Cedeco', 'Redes', 'Soporte Tecnico', 'Laboratorios']
DESCRIPCIONES = [
    'Limpieza interna y verificacion de temperatura.',
    'Reemplazo de componente danado tras reporte de incidencia.',
    'Actualizacion de drivers y mantenimiento preventivo programado.',
    'Revision por falla intermitente reportada por el docente.',
    'Diagnostico de hardware por apagados inesperados.',
    'Cambio de pasta termica y limpieza de ventiladores.',
    'Verificacion de conexiones de red y perifericos.',
]


class Command(BaseCommand):
    """Genera datos de prueba consistentes para demostrar el modulo de mantenimiento."""

    help = 'Puebla espacios, equipos, tecnicos y tickets de mantenimiento con datos de prueba.'

    def add_arguments(self, parser):
        parser.add_argument('--espacios', type=int, default=6, help='Cantidad de espacios a generar.')
        parser.add_argument('--equipos', type=int, default=60, help='Cantidad de equipos a generar.')
        parser.add_argument('--tecnicos', type=int, default=8, help='Cantidad de tecnicos a generar.')
        parser.add_argument('--mantenimientos', type=int, default=40, help='Cantidad de tickets de mantenimiento.')
        parser.add_argument('--seed', type=int, default=42, help='Semilla aleatoria para resultados reproducibles.')

    def handle(self, *args, **options):
        random.seed(options['seed'])

        with transaction.atomic():
            espacios = self._crear_espacios(options['espacios'])
            equipos = self._crear_equipos(options['equipos'], espacios)
            tecnicos = self._crear_tecnicos(options['tecnicos'])
            total_mantenimientos = self._crear_mantenimientos(
                options['mantenimientos'], equipos, tecnicos,
            )

        self.stdout.write(self.style.SUCCESS(
            'Datos de prueba generados correctamente:\n'
            f'  Espacios:       {len(espacios)}\n'
            f'  Equipos:        {len(equipos)}\n'
            f'  Tecnicos:       {len(tecnicos)} (contrasena: Tecnico123!)\n'
            f'  Mantenimientos: {total_mantenimientos}\n\n'
            'Sugerencia: crea un administrador con '
            '"python manage.py crear_admin_prueba" para revisar el modulo.'
        ))

    def _crear_espacios(self, cantidad):
        """Crea espacios de forma idempotente usando el codigo como clave."""
        espacios = []
        for i in range(1, cantidad + 1):
            codigo = f'LAB{200 + i}'
            espacio, _ = Espacio.objects.get_or_create(
                codigo_espacio=codigo,
                defaults={
                    'tipo': random.choice(TIPOS_ESPACIO),
                    'pabellon': random.choice(PABELLONES),
                    'piso': f'Piso {random.randint(1, 4)}',
                    'activo': True,
                },
            )
            espacios.append(espacio)
        return espacios

    def _crear_equipos(self, cantidad, espacios):
        """Crea equipos distribuidos entre los espacios generados."""
        equipos = []
        tipos = list(MODELOS_POR_TIPO.keys())
        for i in range(1, cantidad + 1):
            espacio = random.choice(espacios)
            tipo_equipo = random.choice(tipos)
            codigo = f'{espacio.codigo_espacio}-PC{i:03d}'
            equipo, _ = Equipo.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'espacio': espacio,
                    'numero_serie': f'SN-{random.randint(100000, 999999)}-{i:03d}',
                    'numero_mac': f'MAC:{random.randint(10000, 99999)}:{i}',
                    'tipo_equipo': tipo_equipo,
                    'marca': random.choice(MARCAS),
                    'modelo': random.choice(MODELOS_POR_TIPO[tipo_equipo]),
                    'modo_adquisicion': random.choice(['comprado', 'arrendado', 'donado']),
                    'fecha_adquisicion': date.today() - timedelta(days=random.randint(30, 900)),
                    'estado': random.choices(
                        ['en_uso', 'en_mantenimiento', 'dañado', 'de_baja'],
                        weights=[70, 15, 10, 5],
                    )[0],
                },
            )
            equipos.append(equipo)
        return equipos

    def _crear_tecnicos(self, cantidad):
        """Crea usuarios tecnicos con su perfil tecnico asociado."""
        tecnicos = []
        for i in range(1, cantidad + 1):
            correo = f'tecnico{i}@kairos.test'
            usuario, creado = Usuario.objects.get_or_create(
                correo=correo,
                defaults={
                    'username': f'tecnico{i}',
                    'nombre': random.choice(NOMBRES),
                    'apellido': random.choice(APELLIDOS),
                    'rol': 'tecnico',
                    'is_active': True,
                },
            )
            if creado:
                usuario.set_password('Tecnico123!')
                usuario.save()
            perfil, _ = PerfilTecnico.objects.get_or_create(
                usuario=usuario,
                defaults={'area': random.choice(AREAS)},
            )
            tecnicos.append(perfil)
        return tecnicos

    def _crear_mantenimientos(self, cantidad, equipos, tecnicos):
        """Regenera los tickets de mantenimiento de los equipos sembrados."""
        equipo_ids = [equipo.id for equipo in equipos]
        Mantenimiento.objects.filter(equipo_id__in=equipo_ids).delete()

        estados = ['pendiente', 'en_proceso', 'resuelto', 'cancelado']
        pesos = [20, 30, 40, 10]
        creados = 0

        for _ in range(cantidad):
            equipo = random.choice(equipos)
            estado = random.choices(estados, weights=pesos)[0]
            mantenimiento = Mantenimiento.objects.create(
                equipo=equipo,
                fecha=date.today() - timedelta(days=random.randint(0, 200)),
                tipo_mantenimiento=random.choice(['preventivo', 'correctivo']),
                estado=estado,
                descripcion=random.choice(DESCRIPCIONES),
            )
            asignados = random.sample(tecnicos, k=min(random.randint(1, 2), len(tecnicos)))
            TecnicoMantenimiento.objects.bulk_create([
                TecnicoMantenimiento(mantenimiento=mantenimiento, tecnico=tecnico)
                for tecnico in asignados
            ])
            creados += 1

        return creados
