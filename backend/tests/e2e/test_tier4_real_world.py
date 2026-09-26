from django.urls import reverse
from rest_framework import status

from espacios.models import Espacio, EspacioUsuario
from tests.e2e.base import E2EBaseTestCase, requires_m1, requires_m2
from usuarios.models import Usuario


class Tier4RealWorldScenarioTests(E2EBaseTestCase):
    """
    Tier 4: Real-World Scenarios (Flujos de Gestión de Instalaciones Universitarias).
    Simula flujos de ciclo de vida completos, multi-paso y realistas:
    1. Provisión Integral de Campus Universitario (Campus Provisioning)
    2. Delegación Operativa y Mantenimiento Colaborativo (Facility Delegation & Teamwork)
    3. Reestructuración y Cese de Encargado de Piso (Restructuring & Decommissioning)
    4. Segregación Estricta Multi-Sede (Multi-Campus Boundary Isolation)
    """

    @requires_m2
    def test_escenario_1_provision_integral_campus(self):
        """
        Escenario 1: Provisión Integral de Campus Universitario.
        - Se configura Sede Central con Pabellones y Laboratorios.
        - Se asigna Responsable de Sede (Nivel 1).
        - Se asigna Encargado de Pabellón (Nivel 2).
        - Se asigna Técnico de Piso (Nivel 3).
        - Se asigna Docente en Aula (Nivel 4).
        - Verifica que el ambiente refleja al docente directo y a los mandos territoriales heredados.
        """
        self.auth(self.admin)

        # Paso 1: Asignar Responsable de Sede
        res_sede = self.client.post(self.url_asignaciones, {
            'ambito': 'sede',
            'local_id': self.sede_a.id,
            'usuario_id': self.responsable_a.id,
            'tipo_responsabilidad': 'responsable',
        }, format='json')
        self.assertEqual(res_sede.status_code, status.HTTP_201_CREATED)

        # Paso 2: Asignar Encargado de Pabellón A
        res_edif = self.client.post(self.url_asignaciones, {
            'ambito': 'edificio',
            'edificio_id': self.edificio_a1.id,
            'usuario_id': self.tecnico_2.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_edif.status_code, status.HTTP_201_CREATED)

        # Paso 3: Asignar Técnico de Piso 2
        res_piso = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '2',
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_piso.status_code, status.HTTP_201_CREATED)

        # Paso 4: Asignar Docente en LAB-201
        res_esp = self.client.post(self.url_asignaciones, {
            'ambito': 'espacio',
            'espacio_id': self.espacio_a1_p2.id,
            'usuario_id': self.docente_1.id,
            'tipo_responsabilidad': 'docente',
        }, format='json')
        self.assertEqual(res_esp.status_code, status.HTTP_201_CREATED)

        # Paso 5: Consultar detalle de LAB-201
        res_detalle = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p2.id]))
        self.assertEqual(res_detalle.status_code, status.HTTP_200_OK)

        # Docente es encargado directo
        directos = res_detalle.data.get('encargados_directos', [])
        self.assertTrue(any(d.get('usuario', {}).get('id') == self.docente_1.id for d in directos))

        # Técnico de Piso 2 está en heredados
        heredados = res_detalle.data.get('encargados_heredados', [])
        ids_heredados = [h.get('usuario', {}).get('id') if isinstance(h.get('usuario'), dict) else h.get('id') for h in heredados]
        self.assertIn(self.tecnico_1.id, ids_heredados)

    @requires_m2
    def test_escenario_2_delegacion_operativa_y_trabajo_colaborativo(self):
        """
        Escenario 2: Delegación Operativa y Mantenimiento Colaborativo.
        - El responsable de sede delega el Piso 1 al Técnico Tomás (sin supervisor previo).
        - Tomás adquiere automáticamente al Responsable como supervisor en organigrama.
        - Ante una urgencia en LAB-101 (Piso 1), la Técnica Tania (asignada a otro sector)
          atiende la contingencia y accede a la información del espacio sin restricción.
        """
        # Paso 1: Responsable A delega Piso 1 a Técnico 1
        self.assertIsNone(self.tecnico_1.supervisor)
        self.auth(self.responsable_a)

        res_asig = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '1',
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_asig.status_code, status.HTTP_201_CREATED)

        # Paso 2: Verificar articulación de línea de mando
        self.tecnico_1.refresh_from_db()
        self.assertEqual(self.tecnico_1.supervisor, self.responsable_a)

        # Paso 3: Técnica 2 (Tania) colabora en emergencia de LAB-101
        self.auth(self.tecnico_2)
        res_lab = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p1.id]))
        self.assertEqual(res_lab.status_code, status.HTTP_200_OK)
        self.assertEqual(res_lab.data['codigo_espacio'], 'LAB-101')

    @requires_m2
    def test_escenario_3_reestructuracion_y_cese_encargado_piso(self):
        """
        Escenario 3: Reestructuración y Cese de Encargado de Piso.
        - Se retira al técnico de un piso (DELETE lógico).
        - El espacio deja de reportarlo en encargados heredados.
        - Se asigna un nuevo técnico de reemplazo.
        - El espacio actualiza inmediatamente el encargado heredado.
        """
        self.auth(self.admin)

        # Paso 1: Asignar técnico 1 al Piso 3
        res_asig = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '3',
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_asig.status_code, status.HTTP_201_CREATED)
        asig_id = res_asig.data['id']

        # Paso 2: Verificar presencia en LAB-301
        res_pre = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p3.id]))
        heredados_pre = [h.get('usuario', {}).get('id') if isinstance(h.get('usuario'), dict) else h.get('id') for h in res_pre.data.get('encargados_heredados', [])]
        self.assertIn(self.tecnico_1.id, heredados_pre)

        # Paso 3: Retiro del técnico de piso (DELETE)
        res_del = self.client.delete(reverse('espacio-usuario-detail', args=[asig_id]))
        self.assertEqual(res_del.status_code, status.HTTP_204_NO_CONTENT)

        # Paso 4: Verificar que LAB-301 ya no lo reporta
        res_post = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p3.id]))
        heredados_post = [h.get('usuario', {}).get('id') if isinstance(h.get('usuario'), dict) else h.get('id') for h in res_post.data.get('encargados_heredados', [])]
        self.assertNotIn(self.tecnico_1.id, heredados_post)

        # Paso 5: Asignar técnico de reemplazo (tecnico_2)
        res_nuevo = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '3',
            'usuario_id': self.tecnico_2.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_nuevo.status_code, status.HTTP_201_CREATED)

        # Paso 6: LAB-301 reporta al nuevo técnico
        res_final = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p3.id]))
        heredados_final = [h.get('usuario', {}).get('id') if isinstance(h.get('usuario'), dict) else h.get('id') for h in res_final.data.get('encargados_heredados', [])]
        self.assertIn(self.tecnico_2.id, heredados_final)

    @requires_m1
    def test_escenario_4_segregacion_estricta_multi_sede(self):
        """
        Escenario 4: Segregación Estricta Multi-Sede.
        - Campus Huánuco vs Campus Tingo María.
        - Responsable Huánuco opera en Huánuco pero recibe HTTP 403 al intentar tocar Tingo María.
        - Responsable Tingo María opera en Tingo María de manera autónoma.
        """
        # 1. Responsable Huánuco crea en Huánuco (Éxito 201)
        self.auth(self.responsable_a)
        res_huanuco = self.client.post(self.url_asignaciones, {
            'ambito': 'edificio',
            'edificio_id': self.edificio_a1.id,
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_huanuco.status_code, status.HTTP_201_CREATED)

        # 2. Responsable Huánuco intenta asignar en Pabellón Norte de Tingo María (Rechazo 403)
        res_intento_ajeno = self.client.post(self.url_asignaciones, {
            'ambito': 'edificio',
            'edificio_id': self.edificio_b1.id,
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_intento_ajeno.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Responsable Tingo María opera en su sede legítimamente (Éxito 201)
        self.auth(self.responsable_b)
        res_tingo = self.client.post(self.url_asignaciones, {
            'ambito': 'edificio',
            'edificio_id': self.edificio_b1.id,
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_tingo.status_code, status.HTTP_201_CREATED)
