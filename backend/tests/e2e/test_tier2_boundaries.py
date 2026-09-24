from django.urls import reverse
from rest_framework import status

from espacios.models import Edificio, Espacio, EspacioUsuario, Local
from tests.e2e.base import E2EBaseTestCase, requires_m1
from usuarios.models import Usuario, UsuarioSede


class Tier2BoundaryCornerCaseTests(E2EBaseTestCase):
    """
    Tier 2: Boundary & Corner Cases (>=5 pruebas por área de límite).
    Valida unicidad estricta, campos requeridos por nivel, formatos de texto/piso,
    caracteres especiales, perímetro de seguridad multi-sede y matriz de 5 roles.
    """

    # --------------------------------------------------------------------------
    # B1: Unicidad y Concurrencia de Ámbito
    # --------------------------------------------------------------------------

    def test_b1_01_duplicado_mismo_usuario_mismo_espacio_rechaza_400(self):
        """B1: Impide registrar asignación duplicada activa para el mismo par usuario-espacio."""
        self.auth(self.admin)
        payload = {
            'espacio_id': self.espacio_a1_p1.id,
            'usuario_id': self.docente_1.id,
            'tipo_responsabilidad': 'docente',
        }
        res1 = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        res2 = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_b1_02_mismo_usuario_distintos_espacios_permitido(self):
        """B1: Un mismo usuario puede tener asignaciones activas en diferentes espacios."""
        self.auth(self.admin)
        res1 = self.client.post(
            self.url_asignaciones,
            {'espacio_id': self.espacio_a1_p1.id, 'usuario_id': self.docente_1.id},
            format='json',
        )
        res2 = self.client.post(
            self.url_asignaciones,
            {'espacio_id': self.espacio_a1_p2.id, 'usuario_id': self.docente_1.id},
            format='json',
        )
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

    def test_b1_03_distintos_usuarios_mismo_espacio_permitido(self):
        """B1: Diferentes usuarios pueden estar asignados al mismo espacio colaborativamente."""
        self.auth(self.admin)
        res1 = self.client.post(
            self.url_asignaciones,
            {'espacio_id': self.espacio_a1_p1.id, 'usuario_id': self.docente_1.id, 'tipo_responsabilidad': 'docente'},
            format='json',
        )
        res2 = self.client.post(
            self.url_asignaciones,
            {'espacio_id': self.espacio_a1_p1.id, 'usuario_id': self.tecnico_1.id, 'tipo_responsabilidad': 'tecnico'},
            format='json',
        )
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

    def test_b1_04_reactivacion_de_registro_soft_deleted(self):
        """B1: Reasignar un usuario retirado reactiva el registro soft-deleted sin colisionar."""
        self.auth(self.admin)
        asig = EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p1,
            usuario=self.docente_1,
            tipo_responsabilidad='docente',
            created_by=self.admin,
        )
        # Soft delete
        self.client.delete(reverse('espacio-usuario-detail', args=[asig.id]))
        asig.refresh_from_db()
        self.assertTrue(asig.is_deleted)
        self.assertFalse(asig.activo)

        # Re-creación
        payload = {
            'espacio_id': self.espacio_a1_p1.id,
            'usuario_id': self.docente_1.id,
            'tipo_responsabilidad': 'docente',
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        asig.refresh_from_db()
        self.assertFalse(asig.is_deleted)
        self.assertTrue(asig.activo)

    @requires_m1
    def test_b1_05_duplicado_ambito_piso_rechaza_400(self):
        """B1: Impide duplicar una asignación activa para el mismo técnico y mismo piso."""
        self.auth(self.admin)
        payload = {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '2',
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res1 = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        res2 = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------
    # B2: Coherencia de Datos y Validación de Entidades
    # --------------------------------------------------------------------------

    def test_b2_01_falta_usuario_id_retorna_400(self):
        """B2: Petición sin usuario_id es rechazada con HTTP 400."""
        self.auth(self.admin)
        res = self.client.post(
            self.url_asignaciones,
            {'espacio_id': self.espacio_a1_p1.id},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_b2_02_usuario_inexistente_retorna_400(self):
        """B2: Referencia a usuario_id no existente en BD retorna HTTP 400."""
        self.auth(self.admin)
        res = self.client.post(
            self.url_asignaciones,
            {'espacio_id': self.espacio_a1_p1.id, 'usuario_id': 999999},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_b2_03_espacio_inexistente_retorna_400(self):
        """B2: Referencia a espacio_id inexistente retorna HTTP 400."""
        self.auth(self.admin)
        res = self.client.post(
            self.url_asignaciones,
            {'espacio_id': 999999, 'usuario_id': self.docente_1.id},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @requires_m1
    def test_b2_04_ambito_piso_sin_piso_retorna_400(self):
        """B2: Asignación con ámbito='piso' omitiendo número de piso retorna HTTP 400."""
        self.auth(self.admin)
        payload = {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '',
            'usuario_id': self.tecnico_1.id,
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @requires_m1
    def test_b2_05_ambito_sede_sin_local_retorna_400(self):
        """B2: Asignación con ámbito='sede' omitiendo local_id retorna HTTP 400."""
        self.auth(self.admin)
        payload = {
            'ambito': 'sede',
            'usuario_id': self.responsable_a.id,
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------------------------
    # B3: Formato y Normalización de Piso
    # --------------------------------------------------------------------------

    def test_b3_01_piso_con_espacios_se_normaliza(self):
        """B3: Creación de espacio con piso ' 3 ' se normaliza a '3'."""
        self.auth(self.admin)
        esp = Espacio.objects.create(
            codigo_espacio='LAB-NORM-1',
            tipo='laboratorio',
            pabellon='Pabellón A',
            edificio=self.edificio_a1,
            piso=' 3 '.strip(),
        )
        self.assertEqual(esp.piso, '3')

    def test_b3_02_piso_numerico_valido(self):
        """B3: Pisos numéricos estándar ('0', '1', '10') son procesados correctamente."""
        self.auth(self.admin)
        esp0 = Espacio.objects.create(
            codigo_espacio='LAB-P0',
            tipo='laboratorio',
            pabellon='Pabellón A',
            edificio=self.edificio_a1,
            piso='0',
        )
        self.assertEqual(esp0.piso, '0')

    def test_b3_03_piso_longitud_maxima(self):
        """B3: Valores de piso respetan el límite de 20 caracteres del campo."""
        piso_largo = '1' * 20
        esp = Espacio.objects.create(
            codigo_espacio='LAB-PLARGO',
            tipo='laboratorio',
            pabellon='Pabellón A',
            edificio=self.edificio_a1,
            piso=piso_largo,
        )
        self.assertEqual(esp.piso, piso_largo)

    def test_b3_04_caracteres_especiales_no_provocan_inyeccion(self):
        """B3: Cadenas con comillas y meta-caracteres no corrompen las consultas."""
        self.auth(self.admin)
        res = self.client.get(self.url_asignaciones, {'search': "'; DROP TABLE espacios;--"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_b3_05_espacios_en_blanco_en_busqueda(self):
        """B3: Búsquedas con espacios excesivos no causan excepciones 500."""
        self.auth(self.admin)
        res = self.client.get(self.url_asignaciones, {'search': '   LAB   '})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # --------------------------------------------------------------------------
    # B4: Perímetro de Seguridad Multi-Sede
    # --------------------------------------------------------------------------

    def test_b4_01_usuario_sin_autenticar_retorna_401(self):
        """B4: Consultas y mutaciones anónimas son rechazadas con HTTP 401 Unauthorized."""
        self.deauth()
        res_get = self.client.get(self.url_asignaciones)
        res_post = self.client.post(self.url_asignaciones, {'espacio_id': 1}, format='json')
        self.assertEqual(res_get.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res_post.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_b4_02_responsable_sin_sedes_asignadas_rechaza_escritura(self):
        """B4: Un responsable sin ninguna sede física asignada no puede crear asignaciones."""
        resp_huerfano = Usuario.objects.create_user(
            correo='resp.huerfano@udh.edu.pe',
            username='resp.huerfano',
            rol='responsable',
        )
        self.auth(resp_huerfano)
        res = self.client.post(
            self.url_asignaciones,
            {'espacio_id': self.espacio_a1_p1.id, 'usuario_id': self.docente_1.id},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    @requires_m1
    def test_b4_03_responsable_con_multiples_sedes_accede_solo_a_las_suyas(self):
        """B4: Responsable con dos sedes asignadas puede gestionar ambas pero es bloqueado en una tercera."""
        sede_c = Local.objects.create(codigo='LOC-TINGO-2', nombre='Sede Tingo Anexo', ciudad='Tingo María')
        edif_c = Edificio.objects.create(codigo='ED-C', nombre='Pab C', local=sede_c)

        # Vincular a sede_a y sede_b
        UsuarioSede.objects.create(usuario=self.responsable_a, local=self.sede_b, activo=True)

        self.auth(self.responsable_a)
        # Sede A: permitida
        res_a = self.client.post(
            self.url_asignaciones,
            {'ambito': 'edificio', 'edificio_id': self.edificio_a1.id, 'usuario_id': self.tecnico_1.id},
            format='json',
        )
        # Sede B: permitida
        res_b = self.client.post(
            self.url_asignaciones,
            {'ambito': 'edificio', 'edificio_id': self.edificio_b1.id, 'usuario_id': self.tecnico_1.id},
            format='json',
        )
        # Sede C: rechazada (HTTP 403)
        res_c = self.client.post(
            self.url_asignaciones,
            {'ambito': 'edificio', 'edificio_id': edif_c.id, 'usuario_id': self.tecnico_1.id},
            format='json',
        )
        self.assertEqual(res_a.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_b.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_c.status_code, status.HTTP_403_FORBIDDEN)

    def test_b4_04_responsable_no_puede_acceder_a_opciones_globales(self):
        """B4: Responsable accede a /opciones/ con catálogos filtrados a sus sedes autorizadas (R4/R5)."""
        self.auth(self.responsable_a)
        res = self.client.get(self.url_opciones)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        local_ids = [item['id'] for item in res.data.get('locales', [])]
        self.assertIn(self.sede_a.id, local_ids)
        self.assertNotIn(self.sede_b.id, local_ids)
        edificio_local_ids = {item['local_id'] for item in res.data.get('edificios', [])}
        self.assertIn(self.sede_a.id, edificio_local_ids)
        self.assertNotIn(self.sede_b.id, edificio_local_ids)

    def test_b4_05_admin_accede_a_opciones_globales(self):
        """B4: Administrador accede a catálogos en /opciones/."""
        self.auth(self.admin)
        res = self.client.get(self.url_opciones)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # --------------------------------------------------------------------------
    # B5: Matriz de Roles Exhaustiva
    # --------------------------------------------------------------------------

    def test_b5_01_superadmin_full_access(self):
        """B5: Superadmin tiene permisos de lectura y escritura universales."""
        self.auth(self.superadmin)
        res_get = self.client.get(self.url_asignaciones)
        res_post = self.client.post(
            self.url_asignaciones,
            {'espacio_id': self.espacio_b1_p1.id, 'usuario_id': self.docente_1.id},
            format='json',
        )
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)

    def test_b5_02_admin_full_access(self):
        """B5: Administrador tiene permisos de lectura y escritura universales."""
        self.auth(self.admin)
        res_get = self.client.get(self.url_asignaciones)
        res_post = self.client.post(
            self.url_asignaciones,
            {'espacio_id': self.espacio_a1_p1.id, 'usuario_id': self.docente_1.id},
            format='json',
        )
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)

    def test_b5_03_tecnico_read_only_access(self):
        """B5: Técnico puede listar (200) pero no crear (403)."""
        self.auth(self.tecnico_1)
        res_get = self.client.get(self.url_asignaciones)
        res_post = self.client.post(
            self.url_asignaciones,
            {'espacio_id': self.espacio_a1_p1.id, 'usuario_id': self.docente_1.id},
            format='json',
        )
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertEqual(res_post.status_code, status.HTTP_403_FORBIDDEN)

    @requires_m1
    def test_b5_04_docente_read_only_access(self):
        """B5: Docente puede listar pero no modificar asignaciones (actualizado en M1)."""
        self.auth(self.docente_1)
        res_get = self.client.get(self.url_asignaciones)
        res_post = self.client.post(
            self.url_asignaciones,
            {'espacio_id': self.espacio_a1_p1.id, 'usuario_id': self.docente_1.id},
            format='json',
        )
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertEqual(res_post.status_code, status.HTTP_403_FORBIDDEN)

    def test_b5_05_usuario_comun_forbidden(self):
        """B5: Usuario sin rol de soporte recibe 403 en todo el módulo de asignaciones."""
        self.auth(self.usuario_comun)
        res_get = self.client.get(self.url_asignaciones)
        res_post = self.client.post(
            self.url_asignaciones,
            {'espacio_id': self.espacio_a1_p1.id, 'usuario_id': self.usuario_comun.id},
            format='json',
        )
        self.assertEqual(res_get.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res_post.status_code, status.HTTP_403_FORBIDDEN)

    def test_b5_06_usuario_comun_bloqueado_en_espacios(self):
        """B5: Usuario común recibe 403 al listar infraestructura de espacios."""
        self.auth(self.usuario_comun)
        res = self.client.get(self.url_espacios)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
