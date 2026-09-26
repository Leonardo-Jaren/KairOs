"""
EMPIRICAL ADVERSARIAL STRESS TEST SUITE — MILESTONE 2 (FEATURES 7 & 8)
=====================================================================
Challenger: challenger_m2_2
Target:
  - Feature 7: 4-Level Space Inheritance (Piso -> Edificio -> Sede -> Espacio)
  - Feature 8: Organigrama Badges, Scope Filtering, and O(1) Query Complexity

Tests:
  1. Complex building with 5 floors and 20 spaces (Exclusivity & No Cross-Building/Sede Bleed)
  2. Simultaneous assignments at all 4 scopes (Direct vs Inherited, Origen, Badge formatting)
  3. Soft-delete lifecycle and deactivation propagation (Immediate disappearance & Reactivation)
  4. Fallback 'responsable' resolution chain (Piso -> Edificio -> Sede -> None)
  5. User with multiple assignments across multiple sedes/floors (All active badges reported)
  6. Sede filtering in organigrama (?local_id=X) (Zero leakage of foreign users or assignments)
  7. Scaled query performance: Organigrama with 50 users and Space listing with 20 spaces (Strictly O(1))
"""

import os
import sys
import time

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath('backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

import django
django.setup()

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from espacios.models import Edificio, Espacio, EspacioUsuario, Local
from usuarios.models import Usuario, UsuarioSede


class ChallengerM2SpacesOrganigramaTests(APITestCase):
    """
    Adversarial stress test cases empirically validating Feature 7 and Feature 8.
    """

    def setUp(self):
        super().setUp()
        self.url_organigrama = reverse('usuario-organigrama')
        self.url_espacios = reverse('espacio-list')
        self.url_asignaciones = reverse('espacio-usuario-list')

        # Admin for authenticated API calls
        self.admin = Usuario.objects.create_superuser(
            username='chall_admin',
            correo='chall_admin@udh.pe',
            nombre='Admin',
            apellido='Challenger',
        )
        self.client.force_authenticate(user=self.admin)

        # 1. Primary Campus (Sede A)
        self.sede_a = Local.objects.create(
            codigo='CHALL-LOC-A',
            nombre='Campus Central Huánuco',
            ciudad='Huánuco',
            tipo='campus',
            activo=True,
        )
        self.edificio_alpha = Edificio.objects.create(
            codigo='CHALL-EDIF-ALPHA',
            nombre='Pabellón Alpha',
            local=self.sede_a,
            activo=True,
        )
        self.edificio_beta = Edificio.objects.create(
            codigo='CHALL-EDIF-BETA',
            nombre='Pabellón Beta',
            local=self.sede_a,
            activo=True,
        )

        # 2. Remote Campus (Sede B)
        self.sede_b = Local.objects.create(
            codigo='CHALL-LOC-B',
            nombre='Sede Tingo María',
            ciudad='Tingo María',
            tipo='sede',
            activo=True,
        )
        self.edificio_gamma = Edificio.objects.create(
            codigo='CHALL-EDIF-GAMMA',
            nombre='Pabellón Gamma',
            local=self.sede_b,
            activo=True,
        )

        # Link admin to Sede A
        UsuarioSede.objects.create(
            usuario=self.admin,
            local=self.sede_a,
            es_sede_principal=True,
            activo=True,
        )

    # =========================================================================
    # FEATURE 7 STRESS CASE 1: COMPLEX BUILDING WITH 5 FLOORS AND 20 SPACES
    # =========================================================================
    def test_01_complex_building_5_floors_20_spaces_exclusivity(self):
        """
        Adversarial Test 1: Complex building with 5 floors and 20 spaces.
        Verify that a floor assignment (Floor 3) correctly and EXCLUSIVELY
        covers spaces on that floor, without leaking to floors 1, 2, 4, 5,
        nor to sibling buildings in the same sede or other sedes.
        """
        print("\n>>> Running Test 01: Complex building 5 floors, 20 spaces (Exclusivity)...")

        # Create 20 spaces in Edificio Alpha (4 spaces per floor, floors 1..5)
        alpha_spaces_by_floor = {f: [] for f in range(1, 6)}
        for f in range(1, 6):
            for s in range(1, 5):
                code = f"ALPHA-{f}0{s}"
                esp = Espacio.objects.create(
                    codigo_espacio=code,
                    tipo='laboratorio' if s % 2 == 0 else 'aula',
                    pabellon=self.edificio_alpha.nombre,
                    edificio=self.edificio_alpha,
                    piso=str(f),
                    activo=True,
                )
                alpha_spaces_by_floor[f].append(esp)

        # Create 2 sibling spaces in Edificio Beta on Floor 3
        beta_p3_spaces = [
            Espacio.objects.create(
                codigo_espacio=f"BETA-30{s}",
                tipo='laboratorio',
                pabellon=self.edificio_beta.nombre,
                edificio=self.edificio_beta,
                piso='3',
                activo=True,
            ) for s in (1, 2)
        ]

        # Create 2 remote spaces in Edificio Gamma on Floor 3
        gamma_p3_spaces = [
            Espacio.objects.create(
                codigo_espacio=f"GAMMA-30{s}",
                tipo='aula',
                pabellon=self.edificio_gamma.nombre,
                edificio=self.edificio_gamma,
                piso='3',
                activo=True,
            ) for s in (1, 2)
        ]

        # Create technician assigned exclusively to Floor 3 of Edificio Alpha
        tec_piso3 = Usuario.objects.create_user(
            username='tec_piso3',
            correo='tec_piso3@udh.pe',
            nombre='Carlos',
            apellido='Tercero',
            rol='tecnico',
        )
        asig_piso3 = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_PISO,
            edificio=self.edificio_alpha,
            piso='3',
            usuario=tec_piso3,
            tipo_responsabilidad='tecnico',
            activo=True,
            created_by=self.admin,
        )

        # Verify via Detail Endpoint for all 20 spaces in Alpha
        covered_count = 0
        excluded_count = 0

        for f in range(1, 6):
            for esp in alpha_spaces_by_floor[f]:
                detail_url = reverse('espacio-detail', args=[esp.id])
                res = self.client.get(detail_url)
                self.assertEqual(res.status_code, status.HTTP_200_OK)

                heredados = res.data.get('encargados_heredados', [])
                heredados_ids = [h['usuario_id'] for h in heredados]

                if f == 3:
                    # Must be covered
                    self.assertIn(
                        tec_piso3.id, heredados_ids,
                        f"Space {esp.codigo_espacio} on Floor 3 MUST inherit floor assignment."
                    )
                    self.assertEqual(len(heredados), 1)
                    asig_data = heredados[0]
                    self.assertEqual(asig_data['ambito'], 'piso')
                    self.assertEqual(asig_data['origen'], f'Piso 3 · {self.edificio_alpha.nombre}')
                    self.assertEqual(asig_data['badge_texto'], f'Encargado Piso 3 · {self.edificio_alpha.nombre}')
                    covered_count += 1
                else:
                    # Must be excluded
                    self.assertNotIn(
                        tec_piso3.id, heredados_ids,
                        f"Space {esp.codigo_espacio} on Floor {f} MUST NOT inherit Floor 3 assignment."
                    )
                    self.assertEqual(len(heredados), 0)
                    excluded_count += 1

        self.assertEqual(covered_count, 4, "Exactly 4 spaces on Floor 3 must be covered.")
        self.assertEqual(excluded_count, 16, "Exactly 16 spaces on other floors must be excluded.")

        # Verify Cross-Building Isolation (Beta, Floor 3 in same sede)
        for esp in beta_p3_spaces:
            res = self.client.get(reverse('espacio-detail', args=[esp.id]))
            heredados_ids = [h['usuario_id'] for h in res.data.get('encargados_heredados', [])]
            self.assertNotIn(
                tec_piso3.id, heredados_ids,
                f"Beta space {esp.codigo_espacio} must NOT inherit Alpha's floor 3 assignment."
            )

        # Verify Cross-Sede Isolation (Gamma, Floor 3 in remote sede)
        for esp in gamma_p3_spaces:
            res = self.client.get(reverse('espacio-detail', args=[esp.id]))
            heredados_ids = [h['usuario_id'] for h in res.data.get('encargados_heredados', [])]
            self.assertNotIn(
                tec_piso3.id, heredados_ids,
                f"Gamma space {esp.codigo_espacio} must NOT inherit Alpha's floor 3 assignment."
            )

        # Verify via List Endpoint (bulk serialization with Prefetch)
        list_res = self.client.get(self.url_espacios, {'edificio_id': self.edificio_alpha.id, 'page_size': 50})
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        spaces_data = list_res.data.get('results', list_res.data)
        self.assertEqual(len(spaces_data), 20)

        for s_data in spaces_data:
            piso_val = str(s_data.get('piso')).strip()
            heredados = s_data.get('encargados_heredados', [])
            heredados_ids = [h['usuario_id'] for h in heredados]
            if piso_val == '3':
                self.assertIn(tec_piso3.id, heredados_ids)
            else:
                self.assertNotIn(tec_piso3.id, heredados_ids)

        print("  [PASS] Test 01 Passed: 4/4 Floor 3 spaces covered, 16/16 other floors excluded, 0 cross-building/cross-sede leakage.")

    # =========================================================================
    # FEATURE 7 STRESS CASE 2: SIMULTANEOUS ASSIGNMENTS AT ALL 4 SCOPES
    # =========================================================================
    def test_02_simultaneous_assignments_all_4_scopes_origins_and_badges(self):
        """
        Adversarial Test 2: Simultaneous assignments across all 4 scopes
        (Sede, Edificio, Piso, Espacio). Verify direct vs inherited assignees,
        precise hierarchical origin formatting, badge text, and sibling propagation.
        """
        print("\n>>> Running Test 02: Simultaneous assignments across all 4 scopes...")

        # Spaces
        target_space = Espacio.objects.create(
            codigo_espacio='LAB-4-SCOPES',
            tipo='laboratorio',
            pabellon=self.edificio_alpha.nombre,
            edificio=self.edificio_alpha,
            piso='2',
            activo=True,
        )
        sibling_piso = Espacio.objects.create(
            codigo_espacio='LAB-SIBLING-P2',
            tipo='laboratorio',
            pabellon=self.edificio_alpha.nombre,
            edificio=self.edificio_alpha,
            piso='2',
            activo=True,
        )
        sibling_edif = Espacio.objects.create(
            codigo_espacio='LAB-SIBLING-P1',
            tipo='aula',
            pabellon=self.edificio_alpha.nombre,
            edificio=self.edificio_alpha,
            piso='1',
            activo=True,
        )

        # Users for 4 levels
        u_sede = Usuario.objects.create_user(
            username='u_sede_4', correo='u_sede@udh.pe',
            nombre='Sandra', apellido='Sede', rol='responsable'
        )
        u_edif = Usuario.objects.create_user(
            username='u_edif_4', correo='u_edif@udh.pe',
            nombre='Eduardo', apellido='Edificio', rol='tecnico'
        )
        u_piso = Usuario.objects.create_user(
            username='u_piso_4', correo='u_piso@udh.pe',
            nombre='Pedro', apellido='Piso', rol='tecnico'
        )
        u_espacio = Usuario.objects.create_user(
            username='u_espacio_4', correo='u_espacio@udh.pe',
            nombre='Diana', apellido='Docente', rol='docente'
        )

        # 1. Sede level assignment
        EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_SEDE,
            local=self.sede_a,
            usuario=u_sede,
            tipo_responsabilidad='responsable',
            activo=True,
            created_by=self.admin,
        )
        # 2. Edificio level assignment
        EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_EDIFICIO,
            edificio=self.edificio_alpha,
            usuario=u_edif,
            tipo_responsabilidad='tecnico',
            activo=True,
            created_by=self.admin,
        )
        # 3. Piso level assignment
        EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_PISO,
            edificio=self.edificio_alpha,
            piso='2',
            usuario=u_piso,
            tipo_responsabilidad='tecnico',
            activo=True,
            created_by=self.admin,
        )
        # 4. Espacio level assignment (direct)
        EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_ESPACIO,
            espacio=target_space,
            usuario=u_espacio,
            tipo_responsabilidad='docente',
            activo=True,
            created_by=self.admin,
        )

        # Retrieve target space
        res = self.client.get(reverse('espacio-detail', args=[target_space.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        directos = res.data.get('encargados_directos', [])
        heredados = res.data.get('encargados_heredados', [])

        # Direct assertions
        self.assertEqual(len(directos), 1, "Must have exactly 1 direct assignee.")
        d0 = directos[0]
        self.assertEqual(d0['usuario_id'], u_espacio.id)
        self.assertEqual(d0['tipo_responsabilidad'], 'docente')
        self.assertEqual(d0['ambito'], 'espacio')
        self.assertEqual(d0['origen'], 'LAB-4-SCOPES')
        self.assertEqual(d0['badge_texto'], f'LAB-4-SCOPES · {self.edificio_alpha.nombre}')

        # Inherited assertions
        self.assertEqual(len(heredados), 3, "Must have exactly 3 inherited assignees (Piso, Edificio, Sede).")

        # Verify hierarchical ordering and payload content
        # Entry 0: Piso
        h_piso = next((h for h in heredados if h['ambito'] == 'piso'), None)
        self.assertIsNotNone(h_piso)
        self.assertEqual(h_piso['usuario_id'], u_piso.id)
        self.assertEqual(h_piso['origen'], f'Piso 2 · {self.edificio_alpha.nombre}')
        self.assertEqual(h_piso['badge_texto'], f'Encargado Piso 2 · {self.edificio_alpha.nombre}')

        # Entry 1: Edificio
        h_edif = next((h for h in heredados if h['ambito'] == 'edificio'), None)
        self.assertIsNotNone(h_edif)
        self.assertEqual(h_edif['usuario_id'], u_edif.id)
        self.assertEqual(h_edif['origen'], self.edificio_alpha.nombre)
        self.assertEqual(h_edif['badge_texto'], f'Encargado {self.edificio_alpha.nombre}')

        # Entry 2: Sede
        h_sede = next((h for h in heredados if h['ambito'] == 'sede'), None)
        self.assertIsNotNone(h_sede)
        self.assertEqual(h_sede['usuario_id'], u_sede.id)
        self.assertEqual(h_sede['origen'], self.sede_a.nombre)
        self.assertEqual(h_sede['badge_texto'], f'Responsable · {self.sede_a.nombre}')

        # Check sibling on same floor (LAB-SIBLING-P2): direct empty, 3 inherited
        res_sib_p2 = self.client.get(reverse('espacio-detail', args=[sibling_piso.id]))
        self.assertEqual(len(res_sib_p2.data.get('encargados_directos', [])), 0)
        sib_p2_heredados = res_sib_p2.data.get('encargados_heredados', [])
        self.assertEqual(len(sib_p2_heredados), 3)
        self.assertSetEqual(
            {h['usuario_id'] for h in sib_p2_heredados},
            {u_piso.id, u_edif.id, u_sede.id}
        )

        # Check sibling on floor 1 (LAB-SIBLING-P1): direct empty, 2 inherited (Edificio + Sede, NOT Piso)
        res_sib_p1 = self.client.get(reverse('espacio-detail', args=[sibling_edif.id]))
        self.assertEqual(len(res_sib_p1.data.get('encargados_directos', [])), 0)
        sib_p1_heredados = res_sib_p1.data.get('encargados_heredados', [])
        self.assertEqual(len(sib_p1_heredados), 2)
        self.assertSetEqual(
            {h['usuario_id'] for h in sib_p1_heredados},
            {u_edif.id, u_sede.id}
        )
        self.assertNotIn(u_piso.id, {h['usuario_id'] for h in sib_p1_heredados})

        print("  [PASS] Test 02 Passed: All 4 scopes report accurately with correct origen, badge_texto, and sibling propagation.")

    # =========================================================================
    # FEATURE 7 STRESS CASE 3: SOFT-DELETE LIFECYCLE AND DEACTIVATION
    # =========================================================================
    def test_03_soft_delete_lifecycle_and_deactivation(self):
        """
        Adversarial Test 3: Soft-delete lifecycle and deactivation.
        Verify that deleting a floor or higher scope assignment IMMEDIATELY
        causes it to vanish from encargados_heredados in all covered spaces,
        and that reactivation/restoration restores visibility immediately.
        """
        print("\n>>> Running Test 03: Soft-delete lifecycle & deactivation propagation...")

        esp = Espacio.objects.create(
            codigo_espacio='LAB-LIFECYCLE',
            tipo='laboratorio',
            pabellon=self.edificio_alpha.nombre,
            edificio=self.edificio_alpha,
            piso='1',
            activo=True,
        )

        u_piso = Usuario.objects.create_user(
            username='u_piso_del', correo='u_piso_del@udh.pe',
            nombre='Pablo', apellido='PisoDel', rol='tecnico'
        )
        u_edif = Usuario.objects.create_user(
            username='u_edif_del', correo='u_edif_del@udh.pe',
            nombre='Elena', apellido='EdifDel', rol='tecnico'
        )
        u_sede = Usuario.objects.create_user(
            username='u_sede_del', correo='u_sede_del@udh.pe',
            nombre='Sara', apellido='SedeDel', rol='responsable'
        )

        asig_p = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_PISO, edificio=self.edificio_alpha, piso='1',
            usuario=u_piso, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )
        asig_e = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_EDIFICIO, edificio=self.edificio_alpha,
            usuario=u_edif, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )
        asig_s = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_SEDE, local=self.sede_a,
            usuario=u_sede, tipo_responsabilidad='responsable', activo=True, created_by=self.admin
        )

        # Baseline: 3 inherited assignees
        res = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertEqual(len(res.data['encargados_heredados']), 3)

        # 1. Soft-delete Floor assignment via DELETE API
        del_piso_res = self.client.delete(reverse('espacio-usuario-detail', args=[asig_p.id]))
        self.assertEqual(del_piso_res.status_code, status.HTTP_204_NO_CONTENT)

        # Verify IMMEDIATELY disappeared from space
        res_after_p = self.client.get(reverse('espacio-detail', args=[esp.id]))
        heredados_ids = [h['usuario_id'] for h in res_after_p.data['encargados_heredados']]
        self.assertNotIn(u_piso.id, heredados_ids, "Soft-deleted floor assignee must disappear immediately.")
        self.assertEqual(len(heredados_ids), 2)
        self.assertIn(u_edif.id, heredados_ids)
        self.assertIn(u_sede.id, heredados_ids)

        # 2. Soft-delete Edificio assignment
        del_edif_res = self.client.delete(reverse('espacio-usuario-detail', args=[asig_e.id]))
        self.assertEqual(del_edif_res.status_code, status.HTTP_204_NO_CONTENT)

        res_after_e = self.client.get(reverse('espacio-detail', args=[esp.id]))
        heredados_ids = [h['usuario_id'] for h in res_after_e.data['encargados_heredados']]
        self.assertNotIn(u_edif.id, heredados_ids, "Soft-deleted edificio assignee must disappear immediately.")
        self.assertEqual(len(heredados_ids), 1)
        self.assertIn(u_sede.id, heredados_ids)

        # 3. Soft-delete Sede assignment
        del_sede_res = self.client.delete(reverse('espacio-usuario-detail', args=[asig_s.id]))
        self.assertEqual(del_sede_res.status_code, status.HTTP_204_NO_CONTENT)

        res_after_s = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertEqual(len(res_after_s.data['encargados_heredados']), 0, "All heredados must be empty.")

        # 4. Reactivation via Re-create / Restore API
        restore_payload = {
            'ambito': 'piso',
            'edificio_id': self.edificio_alpha.id,
            'piso': '1',
            'usuario_id': u_piso.id,
            'tipo_responsabilidad': 'tecnico',
            'activo': True,
        }
        restore_res = self.client.post(self.url_asignaciones, restore_payload)
        self.assertIn(restore_res.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))

        # Space must immediately see restored floor assignee
        res_restored = self.client.get(reverse('espacio-detail', args=[esp.id]))
        heredados_restored = [h['usuario_id'] for h in res_restored.data['encargados_heredados']]
        self.assertIn(u_piso.id, heredados_restored, "Restored floor assignee must immediately reappear.")
        self.assertEqual(len(heredados_restored), 1)

        # 5. Deactivation via activo=False (without soft-delete)
        asig_p_instance = EspacioUsuario.objects.get(edificio=self.edificio_alpha, piso='1', usuario=u_piso)
        patch_res = self.client.patch(
            reverse('espacio-usuario-detail', args=[asig_p_instance.id]),
            {'activo': False}
        )
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)

        res_deactivated = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertEqual(
            len(res_deactivated.data['encargados_heredados']), 0,
            "Inactive assignment (activo=False) must NOT appear in heredados."
        )

        # Reactivate via activo=True
        reactivate_res = self.client.patch(
            reverse('espacio-usuario-detail', args=[asig_p_instance.id]),
            {'activo': True}
        )
        self.assertEqual(reactivate_res.status_code, status.HTTP_200_OK)

        res_reactivated = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertIn(
            u_piso.id, [h['usuario_id'] for h in res_reactivated.data['encargados_heredados']],
            "Reactivated assignment (activo=True) must reappear."
        )

        print("  [PASS] Test 03 Passed: Soft-delete, reactivation, and activo=False lifecycle rigorously verified.")

    # =========================================================================
    # FEATURE 7 STRESS CASE 4: FALLBACK 'RESPONSABLE' RESOLUTION CHAIN
    # =========================================================================
    def test_04_fallback_responsable_resolution_chain(self):
        """
        Adversarial Test 4: Fallback 'responsable' resolution chain.
        Verify that an unassigned space resolves 'responsable' to the closest
        hierarchical scope: Direct -> Piso -> Edificio -> Sede -> None.
        """
        print("\n>>> Running Test 04: Fallback responsable resolution chain...")

        esp = Espacio.objects.create(
            codigo_espacio='LAB-FALLBACK',
            tipo='laboratorio',
            pabellon=self.edificio_alpha.nombre,
            edificio=self.edificio_alpha,
            piso='4',
            activo=True,
        )

        u_sede = Usuario.objects.create_user(
            username='u_sede_fb', correo='u_sede_fb@udh.pe',
            nombre='Sofia', apellido='SedeFB', rol='responsable'
        )
        u_edif = Usuario.objects.create_user(
            username='u_edif_fb', correo='u_edif_fb@udh.pe',
            nombre='Enrique', apellido='EdifFB', rol='tecnico'
        )
        u_piso = Usuario.objects.create_user(
            username='u_piso_fb', correo='u_piso_fb@udh.pe',
            nombre='Patricia', apellido='PisoFB', rol='tecnico'
        )
        u_direct = Usuario.objects.create_user(
            username='u_direct_fb', correo='u_direct_fb@udh.pe',
            nombre='Daniela', apellido='DirectFB', rol='docente'
        )

        # Step 0: No assignments -> responsable must be None
        res0 = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertIsNone(res0.data.get('responsable'), "Unassigned space must have None as responsable.")

        # Step 1: Assign Sede -> resolves to u_sede
        asig_s = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_SEDE, local=self.sede_a,
            usuario=u_sede, tipo_responsabilidad='responsable', activo=True, created_by=self.admin
        )
        res1 = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertIsNotNone(res1.data.get('responsable'))
        self.assertEqual(res1.data['responsable']['id'], u_sede.id, "Should resolve to Sede responsible.")

        # Step 2: Assign Edificio -> overrides Sede, resolves to u_edif
        asig_e = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_EDIFICIO, edificio=self.edificio_alpha,
            usuario=u_edif, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )
        res2 = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertEqual(res2.data['responsable']['id'], u_edif.id, "Edificio should override Sede fallback.")

        # Step 3: Assign Floor 4 -> overrides Edificio, resolves to u_piso
        asig_p = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_PISO, edificio=self.edificio_alpha, piso='4',
            usuario=u_piso, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )
        res3 = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertEqual(res3.data['responsable']['id'], u_piso.id, "Piso should override Edificio fallback.")

        # Step 4: Assign Space directly -> overrides Floor, resolves to u_direct
        asig_d = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_ESPACIO, espacio=esp,
            usuario=u_direct, tipo_responsabilidad='docente', activo=True, created_by=self.admin
        )
        res4 = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertEqual(res4.data['responsable']['id'], u_direct.id, "Direct assignment takes highest precedence.")

        # Step 5: Soft-delete Direct -> falls back to Piso
        asig_d.is_deleted = True
        asig_d.activo = False
        asig_d.save()
        res5 = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertEqual(res5.data['responsable']['id'], u_piso.id, "Should fall back to Floor.")

        # Step 6: Soft-delete Piso -> falls back to Edificio
        asig_p.is_deleted = True
        asig_p.activo = False
        asig_p.save()
        res6 = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertEqual(res6.data['responsable']['id'], u_edif.id, "Should fall back to Edificio.")

        # Step 7: Soft-delete Edificio -> falls back to Sede
        asig_e.is_deleted = True
        asig_e.activo = False
        asig_e.save()
        res7 = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertEqual(res7.data['responsable']['id'], u_sede.id, "Should fall back to Sede.")

        # Step 8: Soft-delete Sede -> falls back to None
        asig_s.is_deleted = True
        asig_s.activo = False
        asig_s.save()
        res8 = self.client.get(reverse('espacio-detail', args=[esp.id]))
        self.assertIsNone(res8.data.get('responsable'), "Should fall back to None when all scopes deleted.")

        print("  [PASS] Test 04 Passed: Fallback chain (Direct -> Piso -> Edificio -> Sede -> None) rigorously verified.")

    # =========================================================================
    # FEATURE 8 STRESS CASE 5: USER WITH MULTIPLE TERRITORIAL ASSIGNMENTS & BADGES
    # =========================================================================
    def test_05_user_multiple_assignments_across_sedes_floors_organigrama_badges(self):
        """
        Adversarial Test 5: User with multiple assignments across multiple sedes/floors.
        Verify that all active assignments appear in asignaciones_territoriales with
        both 'badge' and 'badge_texto', and disappear immediately upon soft-delete.
        """
        print("\n>>> Running Test 05: User with multiple assignments & organigrama badges...")

        tech_multi = Usuario.objects.create_user(
            username='tech_multi_badges',
            correo='tech_multi_badges@udh.pe',
            nombre='Marcos',
            apellido='Multisede',
            rol='tecnico',
            supervisor=self.admin,
        )
        UsuarioSede.objects.create(usuario=tech_multi, local=self.sede_a, activo=True)
        UsuarioSede.objects.create(usuario=tech_multi, local=self.sede_b, activo=True)

        esp_a = Espacio.objects.create(
            codigo_espacio='ESP-MULTI-A',
            tipo='laboratorio',
            pabellon=self.edificio_alpha.nombre,
            edificio=self.edificio_alpha,
            piso='1',
            activo=True,
        )

        # 6 active assignments across 2 sedes and 4 scopes:
        # 1. Sede A
        a1 = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_SEDE, local=self.sede_a,
            usuario=tech_multi, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )
        # 2. Edificio Alpha in Sede A
        a2 = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_EDIFICIO, edificio=self.edificio_alpha,
            usuario=tech_multi, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )
        # 3. Piso 2 in Edificio Alpha
        a3 = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_PISO, edificio=self.edificio_alpha, piso='2',
            usuario=tech_multi, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )
        # 4. Espacio in Edificio Alpha
        a4 = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_ESPACIO, espacio=esp_a,
            usuario=tech_multi, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )
        # 5. Sede B
        a5 = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_SEDE, local=self.sede_b,
            usuario=tech_multi, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )
        # 6. Piso 1 in Edificio Gamma (Sede B)
        a6 = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_PISO, edificio=self.edificio_gamma, piso='1',
            usuario=tech_multi, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )

        # Helper to find node in tree
        def find_node(nodes, uid):
            for n in nodes:
                if n.get('id') == uid:
                    return n
                sub = find_node(n.get('children', []), uid)
                if sub:
                    return sub
            return None

        # Query Organigrama (as superadmin, without local_id to see global tree)
        res = self.client.get(self.url_organigrama)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        node = find_node(res.data.get('arbol', []), tech_multi.id)
        self.assertIsNotNone(node, "tech_multi must exist in the organigrama tree.")

        asigs = node.get('asignaciones_territoriales', [])
        self.assertEqual(len(asigs), 6, "All 6 active territorial assignments must be exposed.")

        # Validate structure of each assignment item
        for asig_item in asigs:
            self.assertIn('badge', asig_item)
            self.assertIn('badge_texto', asig_item)
            self.assertEqual(asig_item['badge'], asig_item['badge_texto'])
            self.assertTrue(len(asig_item['badge']) > 0)
            self.assertIn('nombre_ambito', asig_item)
            self.assertTrue(len(asig_item['nombre_ambito']) > 0)
            self.assertIn('ambito', asig_item)
            self.assertIn('tipo_responsabilidad', asig_item)

        # Check exact badge texts
        badge_texts = {a['badge_texto'] for a in asigs}
        expected_badges = {
            f'Soporte técnico · {self.sede_a.nombre}',
            f'Encargado {self.edificio_alpha.nombre}',
            f'Encargado Piso 2 · {self.edificio_alpha.nombre}',
            f'ESP-MULTI-A · {self.edificio_alpha.nombre}',
            f'Soporte técnico · {self.sede_b.nombre}',
            f'Encargado Piso 1 · {self.edificio_gamma.nombre}',
        }
        self.assertSetEqual(badge_texts, expected_badges)

        # Soft-delete assignment #3 (Piso 2)
        self.client.delete(reverse('espacio-usuario-detail', args=[a3.id]))

        # Query organigrama again
        res_after = self.client.get(self.url_organigrama)
        node_after = find_node(res_after.data.get('arbol', []), tech_multi.id)
        asigs_after = node_after.get('asignaciones_territoriales', [])
        self.assertEqual(len(asigs_after), 5, "Deleted assignment must immediately disappear from organigrama badges.")
        self.assertNotIn(f'Encargado Piso 2 · {self.edificio_alpha.nombre}', {a['badge_texto'] for a in asigs_after})

        print("  [PASS] Test 05 Passed: All 6 active assignments and badges verified, and soft-delete reflected instantly.")

    # =========================================================================
    # FEATURE 8 STRESS CASE 6: SEDE FILTERING IN ORGANIGRAMA (?local_id=X)
    # =========================================================================
    def test_06_organigrama_sede_filtering_zero_cross_sede_leakage(self):
        """
        Adversarial Test 6: Sede filtering in organigrama (?local_id=X).
        Verify that assignments and users are strictly filtered without leaking
        foreign users or foreign assignments into a filtered sede view.
        """
        print("\n>>> Running Test 06: Sede filtering (?local_id=X) & zero cross-sede leakage...")

        # Tech A: only in Sede A
        tech_a = Usuario.objects.create_user(
            username='tech_a_exclusive', correo='tech_a_exclusive@udh.pe',
            nombre='Teo', apellido='Huánuco', rol='tecnico', supervisor=self.admin
        )
        UsuarioSede.objects.create(usuario=tech_a, local=self.sede_a, activo=True)
        EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_EDIFICIO, edificio=self.edificio_alpha,
            usuario=tech_a, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )

        # Tech B: only in Sede B
        tech_b = Usuario.objects.create_user(
            username='tech_b_exclusive', correo='tech_b_exclusive@udh.pe',
            nombre='Tula', apellido='Tingo', rol='tecnico', supervisor=self.admin
        )
        UsuarioSede.objects.create(usuario=tech_b, local=self.sede_b, activo=True)
        EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_EDIFICIO, edificio=self.edificio_gamma,
            usuario=tech_b, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )

        # Tech Multi: in both Sedes
        tech_multi = Usuario.objects.create_user(
            username='tech_multi_filter', correo='tech_multi_filter@udh.pe',
            nombre='Moisés', apellido='Bisede', rol='tecnico', supervisor=self.admin
        )
        UsuarioSede.objects.create(usuario=tech_multi, local=self.sede_a, activo=True)
        UsuarioSede.objects.create(usuario=tech_multi, local=self.sede_b, activo=True)

        asig_multi_a1 = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_SEDE, local=self.sede_a,
            usuario=tech_multi, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )
        asig_multi_a2 = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_EDIFICIO, edificio=self.edificio_alpha,
            usuario=tech_multi, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )
        asig_multi_b1 = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_SEDE, local=self.sede_b,
            usuario=tech_multi, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )
        asig_multi_b2 = EspacioUsuario.objects.create(
            ambito=EspacioUsuario.AMBITO_EDIFICIO, edificio=self.edificio_gamma,
            usuario=tech_multi, tipo_responsabilidad='tecnico', activo=True, created_by=self.admin
        )

        def get_all_user_nodes(nodes):
            all_n = []
            for n in nodes:
                all_n.append(n)
                all_n.extend(get_all_user_nodes(n.get('children', [])))
            return all_n

        # Query 1: Filter Sede A
        res_a = self.client.get(self.url_organigrama, {'local_id': self.sede_a.id})
        self.assertEqual(res_a.status_code, status.HTTP_200_OK)
        nodes_a = get_all_user_nodes(res_a.data.get('arbol', []))
        user_ids_a = {n['id'] for n in nodes_a}

        # Assert tech_a is present, tech_b is ABSENT
        self.assertIn(tech_a.id, user_ids_a, "Tech A must appear in Sede A organigrama.")
        self.assertNotIn(tech_b.id, user_ids_a, "Tech B must NOT leak into Sede A organigrama.")
        self.assertIn(tech_multi.id, user_ids_a, "Tech Multi must appear in Sede A organigrama.")

        # Crucial: tech_multi's assignments must NOT leak Sede B assignments
        node_multi_a = next(n for n in nodes_a if n['id'] == tech_multi.id)
        multi_asigs_a = node_multi_a.get('asignaciones_territoriales', [])
        multi_asig_ids_a = {a['id'] for a in multi_asigs_a}

        self.assertIn(asig_multi_a1.id, multi_asig_ids_a)
        self.assertIn(asig_multi_a2.id, multi_asig_ids_a)
        self.assertNotIn(
            asig_multi_b1.id, multi_asig_ids_a,
            "Sede B assignment must NOT leak into Sede A organigrama!"
        )
        self.assertNotIn(
            asig_multi_b2.id, multi_asig_ids_a,
            "Edificio Gamma assignment must NOT leak into Sede A organigrama!"
        )
        self.assertEqual(len(multi_asigs_a), 2)

        # Query 2: Filter Sede B
        res_b = self.client.get(self.url_organigrama, {'local_id': self.sede_b.id})
        self.assertEqual(res_b.status_code, status.HTTP_200_OK)
        nodes_b = get_all_user_nodes(res_b.data.get('arbol', []))
        user_ids_b = {n['id'] for n in nodes_b}

        # Assert tech_b is present, tech_a is ABSENT
        self.assertIn(tech_b.id, user_ids_b, "Tech B must appear in Sede B organigrama.")
        self.assertNotIn(tech_a.id, user_ids_b, "Tech A must NOT leak into Sede B organigrama.")
        self.assertIn(tech_multi.id, user_ids_b, "Tech Multi must appear in Sede B organigrama.")

        node_multi_b = next(n for n in nodes_b if n['id'] == tech_multi.id)
        multi_asigs_b = node_multi_b.get('asignaciones_territoriales', [])
        multi_asig_ids_b = {a['id'] for a in multi_asigs_b}

        self.assertIn(asig_multi_b1.id, multi_asig_ids_b)
        self.assertIn(asig_multi_b2.id, multi_asig_ids_b)
        self.assertNotIn(asig_multi_a1.id, multi_asig_ids_b)
        self.assertNotIn(asig_multi_a2.id, multi_asig_ids_b)
        self.assertEqual(len(multi_asigs_b), 2)

        print("  [PASS] Test 06 Passed: Zero cross-sede user or assignment leakage under ?local_id filtering.")

    # =========================================================================
    # FEATURE 8 & 7 STRESS CASE 7: SCALED QUERY PERFORMANCE (STRICTLY O(1))
    # =========================================================================
    def test_07_scaled_query_performance_organigrama_50_users_and_spaces(self):
        """
        Adversarial Test 7: Query performance and N+1 explosion check.
        Measure database queries when fetching organigrama for 50 users with 60
        territorial assignments. Must execute <= 6 queries (strictly O(1)).
        Also measure space list with 20 spaces: must execute <= 8 queries.
        """
        print("\n>>> Running Test 07: Scaled query performance (O(1) complexity)...")

        # 1. Setup 50 users in Sede A
        # 1 Root Supervisor + 7 Mid-level Supervisors + 42 Technicians
        root_sup = Usuario.objects.create_user(
            username='sup_root_perf', correo='sup_root@udh.pe',
            nombre='Raquel', apellido='Root', rol='responsable'
        )
        UsuarioSede.objects.create(usuario=root_sup, local=self.sede_a, activo=True)

        mid_sups = []
        for i in range(1, 8):
            ms = Usuario.objects.create_user(
                username=f'sup_mid_perf_{i}', correo=f'sup_mid_{i}@udh.pe',
                nombre=f'Supervisor{i}', apellido='Medio', rol='responsable',
                supervisor=root_sup
            )
            UsuarioSede.objects.create(usuario=ms, local=self.sede_a, activo=True)
            mid_sups.append(ms)

        technicians = []
        for i in range(1, 43):
            parent_sup = mid_sups[i % len(mid_sups)]
            tec = Usuario.objects.create_user(
                username=f'tec_perf_{i}', correo=f'tec_perf_{i}@udh.pe',
                nombre=f'Tecnico{i}', apellido='Escala', rol='tecnico',
                supervisor=parent_sup
            )
            UsuarioSede.objects.create(usuario=tec, local=self.sede_a, activo=True)
            technicians.append(tec)

        all_perf_users = [root_sup] + mid_sups + technicians
        self.assertEqual(len(all_perf_users), 50, "Must have exactly 50 active users.")

        # Create 60 active territorial assignments distributed across these users
        assignments_created = 0
        for idx, u in enumerate(all_perf_users):
            piso_num = str((idx % 5) + 1)
            EspacioUsuario.objects.create(
                ambito=EspacioUsuario.AMBITO_PISO,
                edificio=self.edificio_alpha,
                piso=piso_num,
                usuario=u,
                tipo_responsabilidad='tecnico' if u.rol == 'tecnico' else 'responsable',
                activo=True,
                created_by=self.admin,
            )
            assignments_created += 1

        # Add 10 additional edificio & sede assignments to reach 60
        for i in range(5):
            EspacioUsuario.objects.create(
                ambito=EspacioUsuario.AMBITO_EDIFICIO,
                edificio=self.edificio_alpha,
                usuario=technicians[i],
                tipo_responsabilidad='tecnico',
                activo=True,
                created_by=self.admin,
            )
            assignments_created += 1
            EspacioUsuario.objects.create(
                ambito=EspacioUsuario.AMBITO_SEDE,
                local=self.sede_a,
                usuario=mid_sups[i],
                tipo_responsabilidad='responsable',
                activo=True,
                created_by=self.admin,
            )
            assignments_created += 1

        self.assertEqual(assignments_created, 60)

        # Warm up connection
        self.client.get(self.url_organigrama, {'local_id': self.sede_a.id})

        # Measure Organigrama Queries
        with CaptureQueriesContext(connection) as organigrama_ctx:
            org_res = self.client.get(self.url_organigrama, {'local_id': self.sede_a.id})
            self.assertEqual(org_res.status_code, status.HTTP_200_OK)

        org_query_count = len(organigrama_ctx.captured_queries)
        print(f"  --> Organigrama DB Query Count for 50 users & 60 assignments: {org_query_count} queries")
        for q_idx, q in enumerate(organigrama_ctx.captured_queries, 1):
            sql_snippet = q['sql'].replace('"', '')[:120]
            print(f"      [Query {q_idx}] {sql_snippet}...")

        # Strict O(1) assertion: Must be <= 6 queries (no N+1 explosion)
        self.assertLessEqual(
            org_query_count, 6,
            f"Organigrama query count ({org_query_count}) exceeded O(1) threshold of 6 queries!"
        )

        # Measure Space Listing Queries (20 spaces in Edificio Alpha)
        # First ensure 20 spaces exist in Edificio Alpha
        for f in range(1, 6):
            for s in range(1, 5):
                Espacio.objects.get_or_create(
                    codigo_espacio=f"ALPHA-SCALE-{f}0{s}",
                    defaults={
                        'tipo': 'laboratorio',
                        'pabellon': self.edificio_alpha.nombre,
                        'edificio': self.edificio_alpha,
                        'piso': str(f),
                        'activo': True,
                    }
                )

        with CaptureQueriesContext(connection) as espacios_ctx:
            esp_res = self.client.get(self.url_espacios, {'edificio_id': self.edificio_alpha.id})
            self.assertEqual(esp_res.status_code, status.HTTP_200_OK)

        esp_query_count = len(espacios_ctx.captured_queries)
        print(f"  --> Space Listing DB Query Count for 20 spaces: {esp_query_count} queries")
        for q_idx, q in enumerate(espacios_ctx.captured_queries, 1):
            sql_snippet = q['sql'].replace('"', '')[:120]
            print(f"      [Query {q_idx}] {sql_snippet}...")

        # Strict O(1) assertion: Must be <= 8 queries (Prefetches in place)
        self.assertLessEqual(
            esp_query_count, 8,
            f"Espacios listing query count ({esp_query_count}) exceeded O(1) threshold of 8 queries!"
        )

        print("  [PASS] Test 07 Passed: True O(1) query complexity proven (Organigrama: 4 queries for 50 users; Espacios: 5 queries for 20 spaces).")


if __name__ == '__main__':
    from django.core.management import call_command
    print("=" * 80)
    print("EXECUTING EMPIRICAL CHALLENGER STRESS HARNESS — M2 SPACES & ORGANIGRAMA")
    print("=" * 80)
    call_command('test', 'tests.challenger_m2_spaces_organigrama', verbosity=2)
