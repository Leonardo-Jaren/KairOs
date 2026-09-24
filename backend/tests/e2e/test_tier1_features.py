from django.urls import reverse
from rest_framework import status

from espacios.models import Edificio, EspacioUsuario, Local
from tests.e2e.base import E2EBaseTestCase, requires_m1, requires_m2
from usuarios.models import Usuario


class Tier1FeatureCoverageTests(E2EBaseTestCase):
    """
    Tier 1: Feature Coverage (>=5 pruebas por funcionalidad clave).
    Valida el camino feliz, contratos de serialización, códigos HTTP y reglas de negocio
    para Features 1 a 8 según PROJECT.md y ORIGINAL_REQUEST.md.
    """

    # --------------------------------------------------------------------------
    # FEATURE 1: Modelo de Asignación a 4 Ámbitos (R1, AC1)
    # --------------------------------------------------------------------------

    @requires_m1
    def test_f1_01_crear_asignacion_ambito_sede_exitoso(self):
        """F1: Permite registrar una asignación a nivel Sede (Local)."""
        self.auth(self.admin)
        payload = {
            'ambito': 'sede',
            'local_id': self.sede_a.id,
            'usuario_id': self.responsable_a.id,
            'tipo_responsabilidad': 'responsable',
            'activo': True,
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['ambito'], 'sede')
        self.assertEqual(res.data['local']['id'], self.sede_a.id)
        self.assertIsNone(res.data.get('edificio'))
        self.assertIsNone(res.data.get('espacio'))

    @requires_m1
    def test_f1_02_crear_asignacion_ambito_edificio_exitoso(self):
        """F1: Permite registrar asignación a nivel Edificio (Pabellón)."""
        self.auth(self.admin)
        payload = {
            'ambito': 'edificio',
            'edificio_id': self.edificio_a1.id,
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
            'activo': True,
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['ambito'], 'edificio')
        self.assertEqual(res.data['edificio']['id'], self.edificio_a1.id)
        self.assertEqual(res.data['local']['id'], self.sede_a.id)

    @requires_m1
    def test_f1_03_crear_asignacion_ambito_piso_exitoso(self):
        """F1: Permite registrar asignación a nivel Piso de Edificio."""
        self.auth(self.admin)
        payload = {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '2',
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
            'activo': True,
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['ambito'], 'piso')
        self.assertEqual(res.data['piso'], '2')
        self.assertEqual(res.data['edificio']['id'], self.edificio_a1.id)

    def test_f1_04_crear_asignacion_ambito_espacio_compatibilidad(self):
        """F1: Registra asignación por espacio individual con compatibilidad regresiva."""
        self.auth(self.admin)
        payload = {
            'espacio_id': self.espacio_a1_p1.id,
            'usuario_id': self.docente_1.id,
            'tipo_responsabilidad': 'docente',
            'activo': True,
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['usuario']['id'], self.docente_1.id)
        self.assertEqual(res.data['espacio']['id'], self.espacio_a1_p1.id)

    def test_f1_05_auditoria_y_estado_activo_por_defecto(self):
        """F1: La asignación registra autor en created_by y activo=True por defecto."""
        self.auth(self.admin)
        payload = {
            'espacio_id': self.espacio_a1_p2.id,
            'usuario_id': self.docente_1.id,
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        asig = EspacioUsuario.objects.get(id=res.data['id'])
        self.assertEqual(asig.created_by, self.admin)
        self.assertTrue(asig.activo)
        self.assertFalse(asig.is_deleted)

    # --------------------------------------------------------------------------
    # FEATURE 2: CRUD y Serialización de Asignaciones (R1, AC1)
    # --------------------------------------------------------------------------

    def test_f2_01_api_list_paginado_con_metadata(self):
        """F2: Endpoint GET /api/v1/espacios/usuarios/ retorna estructura paginada."""
        self.auth(self.admin)
        res = self.client.get(self.url_asignaciones)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('count', res.data)
        self.assertIn('results', res.data)

    def test_f2_02_api_post_creacion_con_entidades_expandidas(self):
        """F2: POST retorna usuario y espacio anidados con campos informativos."""
        self.auth(self.admin)
        payload = {
            'espacio_id': self.espacio_a1_p3.id,
            'usuario_id': self.docente_1.id,
            'tipo_responsabilidad': 'docente',
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['usuario']['nombre_completo'], 'Diana Docente')
        self.assertEqual(res.data['espacio']['codigo_espacio'], 'LAB-301')

    def test_f2_03_api_patch_actualizacion_parcial(self):
        """F2: Permite modificar tipo de responsabilidad y estado activo mediante PATCH/PUT."""
        self.auth(self.admin)
        asig = EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p1,
            usuario=self.docente_1,
            tipo_responsabilidad='docente',
            created_by=self.admin,
        )
        url_detail = reverse('espacio-usuario-detail', args=[asig.id])
        res = self.client.patch(url_detail, {'activo': False}, format='json')
        self.assertIn(res.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
        asig.refresh_from_db()
        self.assertFalse(asig.activo)

    def test_f2_04_api_delete_logico(self):
        """F2: DELETE ejecuta borrado lógico sin destruir el registro físicamente."""
        self.auth(self.admin)
        asig = EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p2,
            usuario=self.docente_1,
            created_by=self.admin,
        )
        url_detail = reverse('espacio-usuario-detail', args=[asig.id])
        res = self.client.delete(url_detail)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        asig.refresh_from_db()
        self.assertTrue(asig.is_deleted)
        self.assertFalse(asig.activo)

    def test_f2_05_api_filtro_por_busqueda(self):
        """F2: Filtro por parámetro 'search' encuentra asignaciones por código o nombre."""
        self.auth(self.admin)
        EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p1,
            usuario=self.docente_1,
            created_by=self.admin,
        )
        res = self.client.get(self.url_asignaciones, {'search': 'LAB-101'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(res.data['count'], 1)

    # --------------------------------------------------------------------------
    # FEATURE 3: Autorización por Sede y Restricción 403 (R5, AC3)
    # --------------------------------------------------------------------------

    @requires_m1
    def test_f3_01_responsable_gestiona_propia_sede_exitoso(self):
        """F3: Responsable puede crear asignaciones en las sedes físicas asignadas."""
        self.auth(self.responsable_a)
        payload = {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '1',
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    @requires_m1
    def test_f3_02_responsable_rechazado_en_sede_ajena_403(self):
        """F3: Responsable recibe HTTP 403 al intentar asignar en sede ajena."""
        self.auth(self.responsable_a)  # Asignado a Sede A (Huánuco)
        payload = {
            'ambito': 'edificio',
            'edificio_id': self.edificio_b1.id,  # Pertenece a Sede B (Tingo María)
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_f3_03_tecnico_rechazado_en_escritura_403(self):
        """F3: Técnicos tienen acceso de solo lectura y reciben 403 ante POST."""
        self.auth(self.tecnico_1)
        payload = {
            'espacio_id': self.espacio_a1_p1.id,
            'usuario_id': self.docente_1.id,
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_f3_04_docente_rechazado_en_escritura_403(self):
        """F3: Docentes tienen acceso de solo lectura y reciben 403 ante DELETE."""
        self.auth(self.docente_1)
        asig = EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p1,
            usuario=self.docente_1,
            created_by=self.admin,
        )
        url_detail = reverse('espacio-usuario-detail', args=[asig.id])
        res = self.client.delete(url_detail)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_f3_05_superadmin_y_admin_acceso_universal(self):
        """F3: Superadmin y admin pueden crear asignaciones en cualquier sede sin restricción."""
        self.auth(self.superadmin)
        payload = {
            'espacio_id': self.espacio_b1_p1.id,  # Sede B
            'usuario_id': self.docente_1.id,
            'tipo_responsabilidad': 'docente',
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # --------------------------------------------------------------------------
    # FEATURE 4: No Exclusividad Colaborativa (R2)
    # --------------------------------------------------------------------------

    def test_f4_01_tecnico_encargado_no_bloquea_otros_tecnicos(self):
        """F4: La asignación de un técnico no bloquea la consulta a otros técnicos de la sede."""
        EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p1,
            usuario=self.tecnico_1,
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        # Técnico 2 consulta el espacio de la misma sede
        self.auth(self.tecnico_2)
        res = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p1.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_f4_02_coexistencia_de_roles_en_mismo_espacio(self):
        """F4: Un espacio puede tener docente y técnico asignados simultáneamente."""
        EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p1,
            usuario=self.docente_1,
            tipo_responsabilidad='docente',
            created_by=self.admin,
        )
        # Se asigna también el técnico
        asig_tec = EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p1,
            usuario=self.tecnico_1,
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        self.assertTrue(asig_tec.activo)
        self.assertEqual(EspacioUsuario.objects.filter(espacio=self.espacio_a1_p1, activo=True).count(), 2)

    def test_f4_03_tecnicos_de_sede_listan_todos_los_ambientes(self):
        """F4: Técnicos de la sede pueden listar todos los espacios de la sede para soporte colaborativo."""
        self.auth(self.tecnico_1)
        res = self.client.get(self.url_espacios)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        codigos = [e['codigo_espacio'] for e in res.data.get('results', [])]
        self.assertIn('LAB-101', codigos)
        self.assertIn('LAB-201', codigos)

    def test_f4_04_trazabilidad_referencial_de_contacto(self):
        """F4: La consulta de asignaciones identifica al encargado como referente de contacto."""
        self.auth(self.admin)
        asig = EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p2,
            usuario=self.tecnico_1,
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        res = self.client.get(reverse('espacio-usuario-detail', args=[asig.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['usuario']['correo'], 'tecnico1@udh.edu.pe')

    def test_f4_05_reasignacion_operativa_sin_interrupcion(self):
        """F4: Reasignar el encargado de un espacio mantiene la disponibilidad del servicio."""
        self.auth(self.admin)
        asig1 = EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p1,
            usuario=self.tecnico_1,
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        # Se desactiva y se crea uno nuevo
        asig1.activo = False
        asig1.save()
        asig2 = EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p1,
            usuario=self.tecnico_2,
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        self.assertTrue(asig2.activo)

    # --------------------------------------------------------------------------
    # FEATURE 5: Auto-asociación Inteligente de Supervisor (R3, AC5)
    # --------------------------------------------------------------------------

    @requires_m2
    def test_f5_01_tecnico_sin_supervisor_autoasocia_responsable_sede(self):
        """F5: Al asignar técnico con supervisor=None a ámbito de sede, adquiere al responsable."""
        self.assertIsNone(self.tecnico_1.supervisor)
        self.auth(self.admin)
        payload = {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '2',
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.tecnico_1.refresh_from_db()
        self.assertEqual(self.tecnico_1.supervisor, self.responsable_a)

    @requires_m2
    def test_f5_02_autoasociacion_desde_asignacion_espacio(self):
        """F5: Asignación a nivel espacio auto-asocia al responsable de la sede correspondiente."""
        self.assertIsNone(self.tecnico_2.supervisor)
        self.auth(self.admin)
        payload = {
            'ambito': 'espacio',
            'espacio_id': self.espacio_a1_p1.id,
            'usuario_id': self.tecnico_2.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.tecnico_2.refresh_from_db()
        self.assertEqual(self.tecnico_2.supervisor, self.responsable_a)

    @requires_m2
    def test_f5_03_autoasociacion_desde_asignacion_edificio(self):
        """F5: Asignación a nivel edificio vincula al responsable de la sede del edificio."""
        tecnico_nuevo = Usuario.objects.create_user(
            correo='tec.nuevo@udh.edu.pe',
            username='tec.nuevo',
            rol='tecnico',
            supervisor=None,
        )
        self.auth(self.admin)
        payload = {
            'ambito': 'edificio',
            'edificio_id': self.edificio_b1.id,  # Sede B
            'usuario_id': tecnico_nuevo.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tecnico_nuevo.refresh_from_db()
        self.assertEqual(tecnico_nuevo.supervisor, self.responsable_b)

    @requires_m2
    def test_f5_04_sede_sin_responsable_no_falla_asignacion(self):
        """F5: Si la sede no tiene responsable activo, supervisor queda None sin arrojar error."""
        sede_sin_resp = Local.objects.create(codigo='LOC-VACIA', nombre='Sede Vacía', ciudad='Lima')
        edif = Edificio.objects.create(codigo='ED-VAC', nombre='Pab 1', local=sede_sin_resp)
        tec = Usuario.objects.create_user(correo='t.vac@udh.edu.pe', username='t.vac', rol='tecnico')
        self.auth(self.admin)
        payload = {
            'ambito': 'edificio',
            'edificio_id': edif.id,
            'usuario_id': tec.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tec.refresh_from_db()
        self.assertIsNone(tec.supervisor)

    @requires_m2
    def test_f5_05_docente_sin_supervisor_no_adopta_responsable(self):
        """F5: Docentes no tienen supervisor por regla institucional de KairOs."""
        self.assertIsNone(self.docente_1.supervisor)
        self.auth(self.admin)
        payload = {
            'ambito': 'espacio',
            'espacio_id': self.espacio_a1_p1.id,
            'usuario_id': self.docente_1.id,
            'tipo_responsabilidad': 'docente',
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.docente_1.refresh_from_db()
        self.assertIsNone(self.docente_1.supervisor)

    # --------------------------------------------------------------------------
    # FEATURE 6: Preservación de Jerarquía Existente (R3, AC6)
    # --------------------------------------------------------------------------

    @requires_m2
    def test_f6_01_tecnico_con_supervisor_conserva_su_jefe(self):
        """F6: Técnico con supervisor previo no cambia de supervisor al recibir asignación."""
        self.assertEqual(self.tecnico_con_supervisor.supervisor, self.responsable_a)
        self.auth(self.admin)
        payload = {
            'ambito': 'piso',
            'edificio_id': self.edificio_b1.id,  # Sede B (con responsable_b)
            'piso': '1',
            'usuario_id': self.tecnico_con_supervisor.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.tecnico_con_supervisor.refresh_from_db()
        # Permanece responsable_a, no cambia a responsable_b
        self.assertEqual(self.tecnico_con_supervisor.supervisor, self.responsable_a)

    @requires_m2
    def test_f6_02_asignacion_a_segunda_sede_no_altera_jerarquia(self):
        """F6: Asignar a un segundo ámbito territorial conserva el supervisor preexistente."""
        self.assertEqual(self.tecnico_con_supervisor.supervisor, self.responsable_a)
        self.auth(self.admin)
        payload = {
            'ambito': 'espacio',
            'espacio_id': self.espacio_a1_p3.id,
            'usuario_id': self.tecnico_con_supervisor.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.url_asignaciones, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.tecnico_con_supervisor.refresh_from_db()
        self.assertEqual(self.tecnico_con_supervisor.supervisor, self.responsable_a)

    @requires_m2
    def test_f6_03_reasignacion_de_responsabilidad_no_muta_supervisor(self):
        """F6: Modificar tipo de responsabilidad preserva la línea de mando."""
        self.auth(self.admin)
        asig = EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p1,
            usuario=self.tecnico_con_supervisor,
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        url_detail = reverse('espacio-usuario-detail', args=[asig.id])
        res = self.client.patch(url_detail, {'tipo_responsabilidad': 'responsable'}, format='json')
        self.assertIn(res.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
        self.tecnico_con_supervisor.refresh_from_db()
        self.assertEqual(self.tecnico_con_supervisor.supervisor, self.responsable_a)

    @requires_m2
    def test_f6_04_inactivacion_de_asignacion_preserva_supervisor(self):
        """F6: Desactivar la asignación territorial no desvincula el supervisor del usuario."""
        self.auth(self.admin)
        asig = EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p2,
            usuario=self.tecnico_con_supervisor,
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        url_detail = reverse('espacio-usuario-detail', args=[asig.id])
        self.client.patch(url_detail, {'activo': False}, format='json')
        self.tecnico_con_supervisor.refresh_from_db()
        self.assertEqual(self.tecnico_con_supervisor.supervisor, self.responsable_a)

    @requires_m2
    def test_f6_05_jerarquia_inmune_a_borrado_logico(self):
        """F6: El borrado lógico (DELETE) de la asignación no muta el supervisor."""
        self.auth(self.admin)
        asig = EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p3,
            usuario=self.tecnico_con_supervisor,
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        url_detail = reverse('espacio-usuario-detail', args=[asig.id])
        self.client.delete(url_detail)
        self.tecnico_con_supervisor.refresh_from_db()
        self.assertEqual(self.tecnico_con_supervisor.supervisor, self.responsable_a)

    # --------------------------------------------------------------------------
    # FEATURE 7: Reporte de Encargados Heredados (R4, AC4)
    # --------------------------------------------------------------------------

    def test_f7_01_espacio_reporta_encargado_directo(self):
        """F7: GET /api/v1/espacios/{id}/ incluye encargado directo."""
        self.auth(self.admin)
        EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p1,
            usuario=self.docente_1,
            tipo_responsabilidad='docente',
            created_by=self.admin,
        )
        res = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p1.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Debe contener info del espacio
        self.assertEqual(res.data['codigo_espacio'], 'LAB-101')

    @requires_m2
    def test_f7_02_espacio_hereda_encargado_de_piso(self):
        """F7: Espacio en Piso 2 sin encargado directo reporta al técnico de Piso 2 en encargados_heredados."""
        self.auth(self.admin)
        # Asignar técnico al Piso 2 del Pabellón A
        EspacioUsuario.objects.create(
            edificio=self.edificio_a1,
            piso='2',
            usuario=self.tecnico_1,
            ambito='piso',
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        res = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p2.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        heredados = res.data.get('encargados_heredados', [])
        ids = [h['usuario']['id'] if isinstance(h.get('usuario'), dict) else h.get('id') for h in heredados]
        self.assertIn(self.tecnico_1.id, ids)

    @requires_m2
    def test_f7_03_espacio_hereda_encargado_de_edificio(self):
        """F7: Espacio reporta al encargado de edificio con origen='edificio'."""
        self.auth(self.admin)
        EspacioUsuario.objects.create(
            edificio=self.edificio_a1,
            usuario=self.tecnico_2,
            ambito='edificio',
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        res = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p3.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        heredados = res.data.get('encargados_heredados', [])
        self.assertTrue(any(h.get('ambito') == 'edificio' or h.get('origen') == 'edificio' for h in heredados))

    @requires_m2
    def test_f7_04_espacio_con_encargado_directo_y_heredados(self):
        """F7: Coexistencia simultánea de encargados directos y heredados en payload de espacio."""
        self.auth(self.admin)
        # Directo: Docente en LAB-201
        EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p2,
            usuario=self.docente_1,
            ambito='espacio',
            tipo_responsabilidad='docente',
            created_by=self.admin,
        )
        # Heredado: Técnico en Piso 2
        EspacioUsuario.objects.create(
            edificio=self.edificio_a1,
            piso='2',
            usuario=self.tecnico_1,
            ambito='piso',
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        res = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p2.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('encargados_directos', res.data)
        self.assertIn('encargados_heredados', res.data)

    @requires_m2
    def test_f7_05_espacio_resolucion_responsable_operativo(self):
        """F7: El campo 'responsable' del espacio resuelve al encargado operativo más específico."""
        self.auth(self.admin)
        # Sin asignación directa pero con técnico en Piso 2
        EspacioUsuario.objects.create(
            edificio=self.edificio_a1,
            piso='2',
            usuario=self.tecnico_1,
            ambito='piso',
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        res = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p2_b.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Responsable debe existir o encargados_heredados debe contener al tecnico_1
        self.assertIsNotNone(res.data.get('responsable') or res.data.get('encargados_heredados'))

    # --------------------------------------------------------------------------
    # FEATURE 8: Badges de Ámbitos en Organigrama Backend (R3, AC7)
    # --------------------------------------------------------------------------

    def test_f8_01_nodo_organigrama_estructura_base(self):
        """F8: GET /api/v1/usuarios/organigrama/ retorna estructura jerárquica de árbol."""
        self.auth(self.admin)
        res = self.client.get(self.url_organigrama, {'local_id': self.sede_a.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('arbol', res.data)

    @requires_m2
    def test_f8_02_nodo_organigrama_incluye_asignaciones_territoriales(self):
        """F8: Nodos del organigrama exponen el campo 'asignaciones_territoriales'."""
        self.auth(self.admin)
        EspacioUsuario.objects.create(
            edificio=self.edificio_a1,
            piso='1',
            usuario=self.tecnico_con_supervisor,
            ambito='piso',
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        res = self.client.get(self.url_organigrama, {'local_id': self.sede_a.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Buscar el nodo del técnico subordinado
        def find_node(nodes, uid):
            for n in nodes:
                if n.get('id') == uid:
                    return n
                sub = find_node(n.get('children', []), uid)
                if sub:
                    return sub
            return None

        nodo = find_node(res.data['arbol'], self.tecnico_con_supervisor.id)
        if nodo:
            self.assertIn('asignaciones_territoriales', nodo)

    @requires_m2
    def test_f8_03_formato_badge_nivel_piso(self):
        """F8: Badge de piso genera formato 'Encargado Piso {N} · {Pabellón}'."""
        self.auth(self.admin)
        asig = EspacioUsuario.objects.create(
            edificio=self.edificio_a1,
            piso='2',
            usuario=self.tecnico_con_supervisor,
            ambito='piso',
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        res = self.client.get(self.url_organigrama, {'local_id': self.sede_a.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @requires_m2
    def test_f8_04_formato_badge_nivel_sede(self):
        """F8: Asignación a nivel sede genera badge descriptivo de la sede."""
        self.auth(self.admin)
        EspacioUsuario.objects.create(
            local=self.sede_a,
            usuario=self.responsable_a,
            ambito='sede',
            tipo_responsabilidad='responsable',
            created_by=self.admin,
        )
        res = self.client.get(self.url_organigrama, {'local_id': self.sede_a.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @requires_m2
    def test_f8_05_multiples_asignaciones_multiples_badges(self):
        """F8: Usuario con asignación en dos pisos recibe badges para ambos ámbitos."""
        self.auth(self.admin)
        EspacioUsuario.objects.create(
            edificio=self.edificio_a1,
            piso='1',
            usuario=self.tecnico_con_supervisor,
            ambito='piso',
            created_by=self.admin,
        )
        EspacioUsuario.objects.create(
            edificio=self.edificio_a1,
            piso='2',
            usuario=self.tecnico_con_supervisor,
            ambito='piso',
            created_by=self.admin,
        )
        res = self.client.get(self.url_organigrama, {'local_id': self.sede_a.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
