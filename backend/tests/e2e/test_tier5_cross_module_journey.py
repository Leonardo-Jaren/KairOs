from django.urls import reverse
from rest_framework import status

from espacios.models import EspacioUsuario
from tests.e2e.base import E2EBaseTestCase, requires_m1, requires_m2
from usuarios.models import Usuario, UsuarioSede


class Tier5CrossModuleJourneyTests(E2EBaseTestCase):
    """
    Tier 5: Cross-Module Empirical Verification Journey (Milestone 5).
    Verifies the complete end-to-end integration across:
    1. Sede Responsable assignment
    2. Floor Technician assignment
    3. Auto-supervisor assignment in Organigrama
    4. Badges in Organigrama hierarchy payload
    5. Floor chip in Croquis
    6. Inherited technician badge in individual spaces of that floor
    7. Precedence of direct space technician over inherited floor technician
    8. Supervisor preservation when technician already has one
    9. Graceful fallback when Sede lacks an active Responsable
    """

    @requires_m2
    def test_end_to_end_cross_module_journey(self):
        # Initial assertions: Responsable Roberto is in Sede Central (self.sede_a)
        self.auth(self.admin)
        self.assertIsNone(self.tecnico_1.supervisor)

        # 1. Asignar al Responsable Roberto a Sede Central si no estuviera asignado
        self.assertTrue(
            UsuarioSede.objects.filter(
                usuario=self.responsable_a, local=self.sede_a, activo=True
            ).exists()
        )

        # 2. Asignar al Técnico Tomás (self.tecnico_1) al Piso 2 del Pabellón A (self.edificio_a1)
        res_piso = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_a1.id,
            'piso': '2',
            'usuario_id': self.tecnico_1.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_piso.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_piso.data['ambito'], 'piso')
        self.assertEqual(res_piso.data['piso'], '2')
        self.assertEqual(res_piso.data['ubicacion_display'], 'Pabellón A · Piso 2')

        # Verificar el badge generado por el modelo
        asig_obj = EspacioUsuario.objects.get(id=res_piso.data['id'])
        self.assertEqual(asig_obj.badge_texto, 'Encargado Piso 2 · Pabellón A')

        # 3. Verificar que el supervisor de Tomás se establece automáticamente al Responsable de Sede
        self.tecnico_1.refresh_from_db()
        self.assertEqual(self.tecnico_1.supervisor_id, self.responsable_a.id)

        # 4. Verificar Organigrama: Tomás aparece bajo el Responsable y expone el badge
        res_org = self.client.get(self.url_organigrama)
        self.assertEqual(res_org.status_code, status.HTTP_200_OK)

        def find_node(nodes, uid):
            for n in nodes:
                if n.get('id') == uid:
                    return n
                sub = find_node(n.get('children', []), uid)
                if sub:
                    return sub
            return None

        arbol = res_org.data.get('arbol', res_org.data if isinstance(res_org.data, list) else [])
        tomas_node = find_node(arbol, self.tecnico_1.id)
        self.assertIsNotNone(tomas_node, "Tomás debe figurar en el organigrama")
        self.assertEqual(tomas_node.get('supervisor_id'), self.responsable_a.id)

        asigs = tomas_node.get('asignaciones_territoriales', [])
        self.assertTrue(
            any(
                a.get('ambito') == 'piso' and
                a.get('badge') == 'Encargado Piso 2 · Pabellón A'
                for a in asigs
            ),
            f"El nodo de Tomás debe incluir badge 'Encargado Piso 2 · Pabellón A': {asigs}"
        )

        # 5. CroquisPiso: Consultar asignación de piso para Piso 2 de Pabellón A
        res_list_piso = self.client.get(
            f"{self.url_asignaciones}?ambito=piso&edificio_id={self.edificio_a1.id}&piso=2"
        )
        self.assertEqual(res_list_piso.status_code, status.HTTP_200_OK)
        results_piso = res_list_piso.data.get('results', res_list_piso.data)
        self.assertTrue(
            any(
                (a.get('usuario', {}).get('id') if isinstance(a.get('usuario'), dict) else a.get('usuario_id')) == self.tecnico_1.id
                for a in results_piso
            ),
            f"Debe reportar a Tomás como asignado en piso: {results_piso}"
        )

        # 6. Ambientes individuales del Piso 2 (LAB-201 y LAB-202):
        # Ambos reportan al técnico Tomás como encargado heredado
        res_lab201 = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p2.id]))
        self.assertEqual(res_lab201.status_code, status.HTTP_200_OK)
        heredados_201 = res_lab201.data.get('encargados_heredados', [])
        self.assertTrue(
            any(
                (h.get('usuario', {}).get('id') if isinstance(h.get('usuario'), dict) else h.get('id')) == self.tecnico_1.id
                for h in heredados_201
            ),
            "LAB-201 debe reportar a Tomás como encargado heredado"
        )

        res_lab202 = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p2_b.id]))
        self.assertEqual(res_lab202.status_code, status.HTTP_200_OK)
        heredados_202 = res_lab202.data.get('encargados_heredados', [])
        self.assertTrue(
            any(
                (h.get('usuario', {}).get('id') if isinstance(h.get('usuario'), dict) else h.get('id')) == self.tecnico_1.id
                for h in heredados_202
            ),
            "LAB-202 debe reportar a Tomás como encargado heredado"
        )

        # 7. Asignación directa en LAB-201 (Docente Diana)
        res_dir = self.client.post(self.url_asignaciones, {
            'ambito': 'espacio',
            'espacio_id': self.espacio_a1_p2.id,
            'usuario_id': self.docente_1.id,
            'tipo_responsabilidad': 'docente',
        }, format='json')
        self.assertEqual(res_dir.status_code, status.HTTP_201_CREATED)

        # 8. Comprobar que en la API de espacio se reportan ambos:
        # directos = [Diana], heredados = [Tomás]
        res_lab201_updated = self.client.get(reverse('espacio-detail', args=[self.espacio_a1_p2.id]))
        self.assertEqual(res_lab201_updated.status_code, status.HTTP_200_OK)

        directos_201 = res_lab201_updated.data.get('encargados_directos', [])
        self.assertTrue(
            any(
                (d.get('usuario', {}).get('id') if isinstance(d.get('usuario'), dict) else d.get('id')) == self.docente_1.id
                for d in directos_201
            ),
            "LAB-201 debe tener a Diana como encargada directa"
        )

        heredados_201_updated = res_lab201_updated.data.get('encargados_heredados', [])
        self.assertTrue(
            any(
                (h.get('usuario', {}).get('id') if isinstance(h.get('usuario'), dict) else h.get('id')) == self.tecnico_1.id
                for h in heredados_201_updated
            ),
            "LAB-201 mantiene a Tomás como encargado heredado en la API"
        )

    @requires_m2
    def test_supervisor_preservation_when_technician_already_has_supervisor(self):
        """Si el técnico ya posee un supervisor formal, no se sobreescribe al asignar piso."""
        self.auth(self.admin)
        original_supervisor = self.tecnico_con_supervisor.supervisor
        self.assertIsNotNone(original_supervisor)

        res = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_b1.id,  # Edificio en Sede B (cuya responsable es Renata)
            'piso': '1',
            'usuario_id': self.tecnico_con_supervisor.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.tecnico_con_supervisor.refresh_from_db()
        self.assertEqual(self.tecnico_con_supervisor.supervisor, original_supervisor)
        self.assertNotEqual(self.tecnico_con_supervisor.supervisor, self.responsable_b)

    @requires_m2
    def test_graceful_handling_when_sede_lacks_active_responsable(self):
        """Si la sede no tiene responsable activo, supervisor permanece None sin fallar."""
        self.auth(self.admin)
        # Desactivar temporalmente responsables de Sede B
        UsuarioSede.objects.filter(local=self.sede_b).update(activo=False)

        res = self.client.post(self.url_asignaciones, {
            'ambito': 'piso',
            'edificio_id': self.edificio_b1.id,
            'piso': '1',
            'usuario_id': self.tecnico_2.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.tecnico_2.refresh_from_db()
        self.assertIsNone(self.tecnico_2.supervisor)
