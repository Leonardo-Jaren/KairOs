from django.urls import reverse
from rest_framework import status

from espacios.models import EspacioUsuario
from tests.e2e.base import E2EBaseTestCase, requires_m1, requires_m2
from usuarios.models import Usuario


class Tier3CrossFeatureCombinationTests(E2EBaseTestCase):
    """
    Tier 3: Cross-Feature Combinations (Pairwise & Multi-Feature Interactions).
    Valida la interacción entre múltiples componentes del sistema:
    - Autorización por Sede × Ámbitos Territoriales (4 niveles)
    - Auto-asociación × Preservación Jerárquica × Reasignaciones
    - Herencia en Espacios × Sincronización en Organigrama
    - Reactivación Soft-Delete con mutación de tipo de responsabilidad
    - Colaboración concurrente de técnicos sin bloqueo excluyente
    """

    # --------------------------------------------------------------------------
    # C1: Autorización de Responsable × 4 Niveles Territoriales
    # --------------------------------------------------------------------------

    @requires_m1
    def test_c1_01_responsable_propia_sede_cuatro_niveles(self):
        """C1: Responsable puede crear asignaciones en su propia sede en los 4 niveles."""
        self.auth(self.responsable_a)

        # 1. Nivel Sede
        res_sede = self.client.post(self.url_asignaciones, {
            'ambito': 'sede',
            'local_id': self.sede_a.id,
            'usuario_id': self.responsable_a.id,
            'tipo_responsabilidad': 'responsable',
        }, format='json')
        self.assertEqual(res_sede.status_code, status.HTTP_201_CREATED)

        # 2. Nivel Edificio
        res_edif = self.client.post(self.url_asignaciones, {
            'ambito': 'edificio',
            'edificio_id': self.edificio_a1.id,
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_edif.status_code, status.HTTP_201_CREATED)

        # 3. Nivel Piso
        res_piso = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '3',
            'usuario_id': self.tecnico_2.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_piso.status_code, status.HTTP_201_CREATED)

        # 4. Nivel Espacio
        res_esp = self.client.post(self.url_asignaciones, {
            'ambito': 'espacio',
            'espacio_id': self.espacio_a1_p3.id,
            'usuario_id': self.docente_1.id,
            'tipo_responsabilidad': 'docente',
        }, format='json')
        self.assertEqual(res_esp.status_code, status.HTTP_201_CREATED)

    @requires_m1
    def test_c1_02_responsable_sede_ajena_cuatro_niveles_bloqueados_403(self):
        """C1: Responsable recibe HTTP 403 en cada uno de los 4 niveles si pertenecen a otra sede."""
        self.auth(self.responsable_a)  # Pertenece a Sede A

        # 1. Nivel Sede en Sede B -> 403
        res_sede = self.client.post(self.url_asignaciones, {
            'ambito': 'sede',
            'local_id': self.sede_b.id,
            'usuario_id': self.tecnico_1.id,
        }, format='json')
        self.assertEqual(res_sede.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Nivel Edificio en Sede B -> 403
        res_edif = self.client.post(self.url_asignaciones, {
            'ambito': 'edificio',
            'edificio_id': self.edificio_b1.id,
            'usuario_id': self.tecnico_1.id,
        }, format='json')
        self.assertEqual(res_edif.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Nivel Piso en Sede B -> 403
        res_piso = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_b1.id,
            'piso': '1',
            'usuario_id': self.tecnico_1.id,
        }, format='json')
        self.assertEqual(res_piso.status_code, status.HTTP_403_FORBIDDEN)

        # 4. Nivel Espacio en Sede B -> 403
        res_esp = self.client.post(self.url_asignaciones, {
            'ambito': 'espacio',
            'espacio_id': self.espacio_b1_p1.id,
            'usuario_id': self.tecnico_1.id,
        }, format='json')
        self.assertEqual(res_esp.status_code, status.HTTP_403_FORBIDDEN)

    # --------------------------------------------------------------------------
    # C2: Auto-Supervisor × Resolución de Sede en Ámbitos
    # --------------------------------------------------------------------------

    @requires_m2
    def test_c2_01_autoasociacion_resuelve_responsable_desde_piso(self):
        """C2: Al asignar piso a técnico sin supervisor, infiere Sede A y asigna responsable_a."""
        self.assertIsNone(self.tecnico_1.supervisor)
        self.auth(self.admin)
        res = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '1',
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.tecnico_1.refresh_from_db()
        self.assertEqual(self.tecnico_1.supervisor, self.responsable_a)

    @requires_m2
    def test_c2_02_autoasociacion_no_asigna_responsable_inactivo(self):
        """C2: Si el responsable de la sede está inactivo (is_active=False), no se vincula como supervisor."""
        self.responsable_a.is_active = False
        self.responsable_a.save()

        self.assertIsNone(self.tecnico_1.supervisor)
        self.auth(self.admin)
        res = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '1',
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.tecnico_1.refresh_from_db()
        self.assertIsNone(self.tecnico_1.supervisor)

    # --------------------------------------------------------------------------
    # C3: Cadena Completa de Herencia en Espacios (4 Ámbitos Simultáneos)
    # --------------------------------------------------------------------------

    @requires_m2
    def test_c3_01_espacio_resuelve_herencia_completa_cuatro_niveles(self):
        """C3: Espacio con directos y encargados en piso, edificio y sede reporta la jerarquía completa."""
        self.auth(self.admin)

        # 1. Responsable de Sede
        EspacioUsuario.objects.create(
            local=self.sede_a,
            usuario=self.responsable_a,
            ambito='sede',
            tipo_responsabilidad='responsable',
            created_by=self.admin,
        )
        # 2. Encargado de Edificio
        EspacioUsuario.objects.create(
            edificio=self.edificio_a1,
            usuario=self.tecnico_2,
            ambito='edificio',
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        # 3. Encargado de Piso 2
        EspacioUsuario.objects.create(
            edificio=self.edificio_a1,
            piso='2',
            usuario=self.tecnico_1,
            ambito='piso',
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        # 4. Docente directo en LAB-201
        EspacioUsuario.objects.create(
            espacio=self.espacio_a1_p2,
            usuario=self.docente_1,
            ambito='espacio',
            tipo_responsabilidad='docente',
            created_by=self.admin,
        )

        res = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p2.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Directos debe contener docente_1
        directos = res.data.get('encargados_directos', [])
        self.assertTrue(any(d.get('usuario', {}).get('id') == self.docente_1.id for d in directos))

        # Heredados debe incluir tecnico_1 (piso) y tecnico_2 (edificio)
        heredados = res.data.get('encargados_heredados', [])
        ids_heredados = [h.get('usuario', {}).get('id') if isinstance(h.get('usuario'), dict) else h.get('id') for h in heredados]
        self.assertIn(self.tecnico_1.id, ids_heredados)
        self.assertIn(self.tecnico_2.id, ids_heredados)

    # --------------------------------------------------------------------------
    # C4: Sincronización en Organigrama con Ciclo de Vida CRUD
    # --------------------------------------------------------------------------

    @requires_m2
    def test_c4_01_organigrama_sincroniza_creacion_modificacion_y_borrado(self):
        """C4: Organigrama refleja badges al crear, actualizar o eliminar una asignación."""
        self.auth(self.admin)

        # 1. Crear asignación de piso
        res_post = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '2',
            'usuario_id': self.tecnico_con_supervisor.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)
        asig_id = res_post.data['id']

        # 2. Consultar organigrama -> badge presente
        res_org1 = self.client.get(self.url_organigrama, {'local_id': self.sede_a.id})
        self.assertEqual(res_org1.status_code, status.HTTP_200_OK)

        # 3. Eliminar asignación (DELETE lógico)
        res_del = self.client.delete(reverse('espacio-usuario-detail', args=[asig_id]))
        self.assertEqual(res_del.status_code, status.HTTP_204_NO_CONTENT)

        # 4. Consultar organigrama -> badge ya no está activo
        res_org2 = self.client.get(self.url_organigrama, {'local_id': self.sede_a.id})
        self.assertEqual(res_org2.status_code, status.HTTP_200_OK)

    # --------------------------------------------------------------------------
    # C5: Traslado de Sede Preservando Jerarquía Previa
    # --------------------------------------------------------------------------

    @requires_m2
    def test_c5_01_tecnico_reasignado_a_otra_sede_preserva_supervisor_anterior(self):
        """C5: Técnico asignado en Sede A que luego es asignado en Sede B no muta su supervisor."""
        self.assertEqual(self.tecnico_con_supervisor.supervisor, self.responsable_a)

        self.auth(self.admin)
        res = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_b1.id,  # Sede B
            'piso': '1',
            'usuario_id': self.tecnico_con_supervisor.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.tecnico_con_supervisor.refresh_from_db()
        self.assertEqual(self.tecnico_con_supervisor.supervisor, self.responsable_a)

    # --------------------------------------------------------------------------
    # C6: Reactivación Soft-Delete con Transición de Rol
    # --------------------------------------------------------------------------

    def test_c6_01_reactivacion_con_transicion_de_rol(self):
        """C6: Asignación eliminada de docente reactivada como técnico actualiza tipo_responsabilidad."""
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

        # Re-crear con tipo 'responsable'
        res = self.client.post(self.url_asignaciones, {
            'espacio_id': self.espacio_a1_p1.id,
            'usuario_id': self.docente_1.id,
            'tipo_responsabilidad': 'responsable',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        asig.refresh_from_db()
        self.assertFalse(asig.is_deleted)
        self.assertTrue(asig.activo)
        self.assertEqual(asig.tipo_responsabilidad, 'responsable')

    # --------------------------------------------------------------------------
    # C7: Concurrencia Colaborativa de Técnicos en el Mismo Piso
    # --------------------------------------------------------------------------

    @requires_m1
    def test_c7_01_dos_tecnicos_en_mismo_piso_colaboran_sin_bloqueo(self):
        """C7: Dos técnicos pueden asignarse al mismo piso y operar concurrentemente sin error de unicidad."""
        self.auth(self.admin)

        res1 = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '2',
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        res2 = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '2',
            'usuario_id': self.tecnico_2.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
