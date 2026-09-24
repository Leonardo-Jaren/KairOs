import os
import unittest
from django.db import connection
from django.urls import reverse
from rest_framework.test import APITestCase

from espacios.models import Edificio, Espacio, EspacioUsuario, Local
from usuarios.models import Usuario, UsuarioSede


def is_strict_mode():
    """Modo estricto: no salta ninguna prueba y evalúa contra la especificación total."""
    return os.environ.get('E2E_STRICT', '0') in ('1', 'true', 'True')


def is_m1_ready():
    """
    Verifica si Milestone 1 está integrado y listo para ser probado:
    1. EspacioUsuarioCreateUpdateSerializer acepta el campo 'ambito'.
    2. La tabla 'espacios_usuarios' en base de datos contiene la columna 'ambito'.
    """
    try:
        from espacios.serializers.espacio_usuario_serializers import EspacioUsuarioCreateUpdateSerializer
        if 'ambito' not in EspacioUsuarioCreateUpdateSerializer().fields:
            return False
        with connection.cursor() as cursor:
            cols = [col.name for col in connection.introspection.get_table_description(cursor, 'espacios_usuarios')]
            if 'ambito' not in cols:
                return False
        return True
    except Exception:
        return False


def is_m2_ready():
    """
    Verifica si Milestone 2 está integrado:
    Requiere M1 listo más la presencia de 'encargados_heredados' en serializadores de espacio.
    """
    if not is_m1_ready():
        return False
    try:
        from espacios.serializers.espacio_serializers import EspacioSerializer
        return 'encargados_heredados' in EspacioSerializer().fields
    except Exception:
        return False


def requires_m1(test_func):
    """Decorator para pruebas con dependencia en Milestone 1."""
    if is_strict_mode():
        return test_func

    def wrapper(self, *args, **kwargs):
        if not is_m1_ready():
            raise unittest.SkipTest('Pendiente de Milestone 1: Modelo, migración y serializador con soporte de ámbito.')
        return test_func(self, *args, **kwargs)

    wrapper.__name__ = test_func.__name__
    wrapper.__doc__ = test_func.__doc__
    return wrapper


def requires_m2(test_func):
    """Decorator para pruebas con dependencia en Milestone 2."""
    if is_strict_mode():
        return test_func

    def wrapper(self, *args, **kwargs):
        if not is_m2_ready():
            raise unittest.SkipTest('Pendiente de Milestone 2: Articulación jerárquica y encargados heredados.')
        return test_func(self, *args, **kwargs)

    wrapper.__name__ = test_func.__name__
    wrapper.__doc__ = test_func.__doc__
    return wrapper


class E2EBaseTestCase(APITestCase):
    """
    Base de pruebas End-to-End para el ecosistema KairOs.
    Configura una infraestructura física completa de dos campus independientes,
    árbol de usuarios con los 5 roles clave, y asignaciones de sede iniciales.
    """

    def setUp(self):
        super().setUp()

        # URLs del sistema
        self.url_asignaciones = reverse('espacio-usuario-list')
        self.url_opciones = reverse('espacio-usuario-opciones')
        self.url_espacios = reverse('espacio-list')
        self.url_edificios = reverse('edificio-list')
        self.url_locales = reverse('local-list')
        self.url_organigrama = reverse('usuario-organigrama')

        # 1. Infraestructura Física - Sede A (Campus Central Huánuco)
        self.sede_a = Local.objects.create(
            codigo='LOC-HUANUCO',
            nombre='Campus Central Huánuco',
            ciudad='Huánuco',
            tipo='campus',
            activo=True,
        )
        self.edificio_a1 = Edificio.objects.create(
            codigo='EDIF-A',
            nombre='Pabellón A',
            local=self.sede_a,
            activo=True,
        )
        self.edificio_a2 = Edificio.objects.create(
            codigo='EDIF-B',
            nombre='Pabellón B',
            local=self.sede_a,
            activo=True,
        )
        self.espacio_a1_p1 = Espacio.objects.create(
            codigo_espacio='LAB-101',
            tipo='laboratorio',
            pabellon='Pabellón A',
            edificio=self.edificio_a1,
            piso='1',
            activo=True,
        )
        self.espacio_a1_p2 = Espacio.objects.create(
            codigo_espacio='LAB-201',
            tipo='laboratorio',
            pabellon='Pabellón A',
            edificio=self.edificio_a1,
            piso='2',
            activo=True,
        )
        self.espacio_a1_p2_b = Espacio.objects.create(
            codigo_espacio='LAB-202',
            tipo='laboratorio',
            pabellon='Pabellón A',
            edificio=self.edificio_a1,
            piso='2',
            activo=True,
        )
        self.espacio_a1_p3 = Espacio.objects.create(
            codigo_espacio='LAB-301',
            tipo='laboratorio',
            pabellon='Pabellón A',
            edificio=self.edificio_a1,
            piso='3',
            activo=True,
        )

        # 2. Infraestructura Física - Sede B (Sede Tingo María)
        self.sede_b = Local.objects.create(
            codigo='LOC-TINGO',
            nombre='Sede Tingo María',
            ciudad='Tingo María',
            tipo='sede',
            activo=True,
        )
        self.edificio_b1 = Edificio.objects.create(
            codigo='EDIF-N',
            nombre='Pabellón Norte',
            local=self.sede_b,
            activo=True,
        )
        self.espacio_b1_p1 = Espacio.objects.create(
            codigo_espacio='LAB-N101',
            tipo='laboratorio',
            pabellon='Pabellón Norte',
            edificio=self.edificio_b1,
            piso='1',
            activo=True,
        )

        # 3. Usuarios de Sistema
        self.superadmin = Usuario.objects.create_user(
            correo='superadmin@udh.edu.pe',
            username='superadmin',
            nombre='Super',
            apellido='Admin',
            rol='superadmin',
            is_superuser=True,
            is_staff=True,
        )
        self.admin = Usuario.objects.create_user(
            correo='admin@udh.edu.pe',
            username='admin',
            nombre='Ada',
            apellido='Admin',
            rol='admin',
            is_staff=True,
        )
        self.responsable_a = Usuario.objects.create_user(
            correo='resp.huanuco@udh.edu.pe',
            username='resp.huanuco',
            nombre='Roberto',
            apellido='Responsable',
            rol='responsable',
            supervisor=self.admin,
        )
        self.responsable_b = Usuario.objects.create_user(
            correo='resp.tingo@udh.edu.pe',
            username='resp.tingo',
            nombre='Renata',
            apellido='Responsable',
            rol='responsable',
            supervisor=self.admin,
        )
        self.tecnico_1 = Usuario.objects.create_user(
            correo='tecnico1@udh.edu.pe',
            username='tecnico1',
            nombre='Tomás',
            apellido='Técnico',
            rol='tecnico',
            supervisor=None,
        )
        self.tecnico_2 = Usuario.objects.create_user(
            correo='tecnico2@udh.edu.pe',
            username='tecnico2',
            nombre='Tania',
            apellido='Torres',
            rol='tecnico',
            supervisor=None,
        )
        self.tecnico_con_supervisor = Usuario.objects.create_user(
            correo='tecnico.sub@udh.edu.pe',
            username='tecnico.sub',
            nombre='Tiago',
            apellido='Subordinado',
            rol='tecnico',
            supervisor=self.responsable_a,
        )
        self.docente_1 = Usuario.objects.create_user(
            correo='docente1@udh.edu.pe',
            username='docente1',
            nombre='Diana',
            apellido='Docente',
            rol='docente',
            supervisor=None,
        )
        self.usuario_comun = Usuario.objects.create_user(
            correo='usuario@udh.edu.pe',
            username='usuario.comun',
            nombre='Ulises',
            apellido='Usuario',
            rol='usuario',
            supervisor=None,
        )

        # 4. Asignaciones de Sede (UsuarioSede)
        UsuarioSede.objects.create(
            usuario=self.responsable_a,
            local=self.sede_a,
            es_sede_principal=True,
            activo=True,
        )
        UsuarioSede.objects.create(
            usuario=self.responsable_b,
            local=self.sede_b,
            es_sede_principal=True,
            activo=True,
        )
        UsuarioSede.objects.create(
            usuario=self.tecnico_1,
            local=self.sede_a,
            es_sede_principal=True,
            activo=True,
        )
        UsuarioSede.objects.create(
            usuario=self.tecnico_2,
            local=self.sede_a,
            es_sede_principal=True,
            activo=True,
        )
        UsuarioSede.objects.create(
            usuario=self.tecnico_con_supervisor,
            local=self.sede_a,
            es_sede_principal=True,
            activo=True,
        )
        UsuarioSede.objects.create(
            usuario=self.docente_1,
            local=self.sede_a,
            es_sede_principal=True,
            activo=True,
        )

    def auth(self, user):
        """Autentica al cliente HTTP con el usuario indicado."""
        self.client.force_authenticate(user=user)

    def deauth(self):
        """Desautentica al cliente HTTP."""
        self.client.force_authenticate(user=None)
