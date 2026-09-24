"""
verify_security_m1_iter2.py
Adversarial Security Verification Suite for Milestone 1 Iteration 2 (R5)
Agent: challenger_m1_iter2_2

Tests all 29 adversarial attack scenarios plus empirical verification of:
- Requirement 2: Operator with 0 active sedes querying GET /api/v1/espacios/usuarios/ gets empty list ([])
- Requirement 3: Responsable accessing GET /api/v1/espacios/usuarios/opciones/ receives HTTP 200 strictly filtered to assigned sedes
"""

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

import django
django.setup()

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from espacios.models import Edificio, Espacio, EspacioUsuario, Local
from usuarios.models import Usuario, UsuarioSede


class AdversarialSecurityM1Iter2Tests(TestCase):
    """
    Adversarial challenge test harness for multi-sede permissions, R5 boundary enforcement,
    and Milestone 1 Iteration 2 remediation verification.
    """

    def setUp(self):
        self.client = APIClient()

        # ── Setup Users ──────────────────────────────────────────────────────────
        self.admin = Usuario.objects.create_user(
            correo='admin.sec.iter2@udh.edu.pe',
            username='admin.sec.iter2',
            nombre='Admin',
            apellido='Security',
            rol='admin',
        )
        self.responsable_a = Usuario.objects.create_user(
            correo='resp.a.iter2@udh.edu.pe',
            username='resp.a.iter2',
            nombre='Responsable',
            apellido='Sede A',
            rol='responsable',
        )
        self.responsable_b = Usuario.objects.create_user(
            correo='resp.b.iter2@udh.edu.pe',
            username='resp.b.iter2',
            nombre='Responsable',
            apellido='Sede B',
            rol='responsable',
        )
        self.tecnico_a = Usuario.objects.create_user(
            correo='tec.a.iter2@udh.edu.pe',
            username='tec.a.iter2',
            nombre='Tecnico',
            apellido='Sede A',
            rol='tecnico',
        )
        self.tecnico_b = Usuario.objects.create_user(
            correo='tec.b.iter2@udh.edu.pe',
            username='tec.b.iter2',
            nombre='Tecnico',
            apellido='Sede B',
            rol='tecnico',
        )
        self.docente = Usuario.objects.create_user(
            correo='docente.iter2@udh.edu.pe',
            username='docente.iter2',
            nombre='Docente',
            apellido='Facultad',
            rol='docente',
        )
        self.usuario_comun = Usuario.objects.create_user(
            correo='estudiante.iter2@udh.edu.pe',
            username='estudiante.iter2',
            nombre='Estudiante',
            apellido='Regular',
            rol='usuario',
        )

        # ── Setup Sedes, Edificios, Espacios ─────────────────────────────────────
        self.sede_a = Local.objects.create(
            codigo='LOC-SEDE-A-IT2',
            nombre='Sede A Campus Huánuco',
            ciudad='Huánuco',
            tipo='sede',
        )
        self.sede_b = Local.objects.create(
            codigo='LOC-SEDE-B-IT2',
            nombre='Sede B Campus Tingo María',
            ciudad='Tingo María',
            tipo='sede',
        )

        self.edificio_a1 = Edificio.objects.create(
            codigo='EDIF-A1-IT2',
            nombre='Pabellón A1',
            local=self.sede_a,
        )
        self.edificio_b1 = Edificio.objects.create(
            codigo='EDIF-B1-IT2',
            nombre='Pabellón B1',
            local=self.sede_b,
        )

        self.espacio_a101 = Espacio.objects.create(
            codigo_espacio='LAB-A101-IT2',
            tipo='laboratorio',
            pabellon='Pabellón A1',
            edificio=self.edificio_a1,
            piso='1',
        )
        self.espacio_b101 = Espacio.objects.create(
            codigo_espacio='LAB-B101-IT2',
            tipo='laboratorio',
            pabellon='Pabellón B1',
            edificio=self.edificio_b1,
            piso='1',
        )

        # ── Link Users to Sedes ──────────────────────────────────────────────────
        self.us_resp_a = UsuarioSede.objects.create(
            usuario=self.responsable_a,
            local=self.sede_a,
            activo=True,
            es_sede_principal=True,
        )
        self.us_resp_b = UsuarioSede.objects.create(
            usuario=self.responsable_b,
            local=self.sede_b,
            activo=True,
            es_sede_principal=True,
        )
        self.us_tec_a = UsuarioSede.objects.create(
            usuario=self.tecnico_a,
            local=self.sede_a,
            activo=True,
            es_sede_principal=True,
        )
        self.us_tec_b = UsuarioSede.objects.create(
            usuario=self.tecnico_b,
            local=self.sede_b,
            activo=True,
            es_sede_principal=True,
        )

        # ── Base Pre-existing Assignments ────────────────────────────────────────
        self.asig_a1 = EspacioUsuario.objects.create(
            ambito='edificio',
            edificio=self.edificio_a1,
            local=self.sede_a,
            usuario=self.tecnico_a,
            tipo_responsabilidad='tecnico',
            activo=True,
            created_by=self.admin,
        )
        self.asig_b1 = EspacioUsuario.objects.create(
            ambito='edificio',
            edificio=self.edificio_b1,
            local=self.sede_b,
            usuario=self.tecnico_b,
            tipo_responsabilidad='tecnico',
            activo=True,
            created_by=self.admin,
        )
        self.asig_b_piso = EspacioUsuario.objects.create(
            ambito='piso',
            edificio=self.edificio_b1,
            local=self.sede_b,
            piso='1',
            usuario=self.tecnico_b,
            tipo_responsabilidad='tecnico',
            activo=True,
            created_by=self.admin,
        )
        self.asig_b_espacio = EspacioUsuario.objects.create(
            ambito='espacio',
            espacio=self.espacio_b101,
            edificio=self.edificio_b1,
            local=self.sede_b,
            piso='1',
            usuario=self.tecnico_b,
            tipo_responsabilidad='tecnico',
            activo=True,
            created_by=self.admin,
        )

        self.list_url = reverse('espacio-usuario-list')
        self.opciones_url = reverse('espacio-usuario-opciones')

    # ══════════════════════════════════════════════════════════════════════════════
    # ATTACK VECTOR 1: Bypass Sede Restrictions (PATCH, PUT, DELETE)
    # ══════════════════════════════════════════════════════════════════════════════

    def test_1_1_responsable_a_cannot_patch_assignment_in_sede_b(self):
        """ATTACK: Responsable Sede A attempts PATCH on Sede B assignment."""
        self.client.force_authenticate(self.responsable_a)
        url = reverse('espacio-usuario-detail', args=[self.asig_b1.id])
        res = self.client.patch(url, {'tipo_responsabilidad': 'docente'}, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.asig_b1.refresh_from_db()
        self.assertEqual(self.asig_b1.tipo_responsabilidad, 'tecnico', 'DB record was modified!')

    def test_1_2_responsable_a_cannot_put_assignment_in_sede_b(self):
        """ATTACK: Responsable Sede A attempts full PUT replacement on Sede B assignment."""
        self.client.force_authenticate(self.responsable_a)
        url = reverse('espacio-usuario-detail', args=[self.asig_b1.id])
        payload = {
            'ambito': 'edificio',
            'edificio_id': self.edificio_b1.id,
            'usuario_id': self.tecnico_b.id,
            'tipo_responsabilidad': 'docente',
            'activo': True,
        }
        res = self.client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.asig_b1.refresh_from_db()
        self.assertEqual(self.asig_b1.tipo_responsabilidad, 'tecnico', 'DB record was modified!')

    def test_1_3_responsable_a_cannot_delete_assignment_in_sede_b(self):
        """ATTACK: Responsable Sede A attempts DELETE on Sede B assignment."""
        self.client.force_authenticate(self.responsable_a)
        url = reverse('espacio-usuario-detail', args=[self.asig_b1.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.asig_b1.refresh_from_db()
        self.assertFalse(self.asig_b1.is_deleted, 'Assignment was soft-deleted!')

    def test_1_4_responsable_a_cannot_patch_sede_b_assignment_by_spoofing_local_id_a_in_body(self):
        """ATTACK: Responsable Sede A sends PATCH targeting Sede B with local_id=Sede_A injected in body."""
        self.client.force_authenticate(self.responsable_a)
        url = reverse('espacio-usuario-detail', args=[self.asig_b1.id])
        res = self.client.patch(
            url,
            {
                'local_id': self.sede_a.id,
                'tipo_responsabilidad': 'docente',
            },
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.asig_b1.refresh_from_db()
        self.assertEqual(self.asig_b1.tipo_responsabilidad, 'tecnico')

    def test_1_5_responsable_a_cannot_move_own_assignment_to_sede_b_via_patch(self):
        """ATTACK: Responsable Sede A attempts PATCH on own assignment to hijack it into Sede B."""
        self.client.force_authenticate(self.responsable_a)
        url = reverse('espacio-usuario-detail', args=[self.asig_a1.id])
        res = self.client.patch(
            url,
            {
                'edificio_id': self.edificio_b1.id,
            },
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.asig_a1.refresh_from_db()
        self.assertEqual(self.asig_a1.edificio_id, self.edificio_a1.id)

    def test_1_6_responsable_cannot_mutate_when_sede_membership_is_inactive(self):
        """ATTACK: Responsable whose UsuarioSede is deactivated attempts mutation in formerly owned sede."""
        self.us_resp_a.activo = False
        self.us_resp_a.save()

        self.client.force_authenticate(self.responsable_a)
        url = reverse('espacio-usuario-detail', args=[self.asig_a1.id])
        res = self.client.patch(url, {'tipo_responsabilidad': 'docente'}, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # ══════════════════════════════════════════════════════════════════════════════
    # ATTACK VECTOR 2: Foreign ID Forging / Hierarchy Bypass
    # ══════════════════════════════════════════════════════════════════════════════

    def test_2_1_responsable_a_cannot_assign_foreign_edificio_directly(self):
        """ATTACK: Responsable Sede A creates assignment with foreign edificio_id without local_id."""
        self.client.force_authenticate(self.responsable_a)
        payload = {
            'ambito': 'edificio',
            'edificio_id': self.edificio_b1.id,
            'usuario_id': self.tecnico_a.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_2_2_responsable_a_cannot_assign_foreign_edificio_by_spoofing_local_id(self):
        """ATTACK: Responsable Sede A sends foreign edificio_id BUT forges local_id=Sede_A to pass permission check."""
        self.client.force_authenticate(self.responsable_a)
        payload = {
            'ambito': 'edificio',
            'local_id': self.sede_a.id,
            'edificio_id': self.edificio_b1.id,
            'usuario_id': self.tecnico_a.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.list_url, payload, format='json')
        self.assertIn(res.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])
        self.assertFalse(
            EspacioUsuario.objects.filter(
                edificio=self.edificio_b1,
                usuario=self.tecnico_a,
            ).exists(),
            'CRITICAL BUG: Assignment created for foreign edificio via local_id forging!'
        )

    def test_2_3_responsable_a_cannot_assign_foreign_piso_by_spoofing_local_id(self):
        """ATTACK: Responsable Sede A assigns foreign piso in Edificio B with forged local_id=Sede_A."""
        self.client.force_authenticate(self.responsable_a)
        payload = {
            'ambito': 'piso',
            'local_id': self.sede_a.id,
            'edificio_id': self.edificio_b1.id,
            'piso': '2',
            'usuario_id': self.tecnico_a.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.list_url, payload, format='json')
        self.assertIn(res.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])
        self.assertFalse(
            EspacioUsuario.objects.filter(
                edificio=self.edificio_b1,
                piso='2',
                usuario=self.tecnico_a,
            ).exists()
        )

    def test_2_4_responsable_a_cannot_assign_foreign_espacio_by_spoofing_local_id(self):
        """ATTACK: Responsable Sede A assigns foreign espacio in Sede B with forged local_id=Sede_A."""
        self.client.force_authenticate(self.responsable_a)
        payload = {
            'ambito': 'espacio',
            'local_id': self.sede_a.id,
            'espacio_id': self.espacio_b101.id,
            'usuario_id': self.tecnico_a.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.list_url, payload, format='json')
        self.assertIn(res.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])
        self.assertFalse(
            EspacioUsuario.objects.filter(
                espacio=self.espacio_b101,
                usuario=self.tecnico_a,
            ).exists()
        )

    # ══════════════════════════════════════════════════════════════════════════════
    # ATTACK VECTOR 3: Privilege Escalation (Tecnico / Docente)
    # ══════════════════════════════════════════════════════════════════════════════

    def test_3_1_tecnico_cannot_perform_post(self):
        """ATTACK: Tecnico forges POST to create an assignment."""
        self.client.force_authenticate(self.tecnico_a)
        payload = {
            'ambito': 'edificio',
            'edificio_id': self.edificio_a1.id,
            'usuario_id': self.tecnico_a.id,
            'tipo_responsabilidad': 'tecnico',
        }
        res = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_3_2_tecnico_cannot_perform_put(self):
        """ATTACK: Tecnico forges PUT on existing assignment."""
        self.client.force_authenticate(self.tecnico_a)
        url = reverse('espacio-usuario-detail', args=[self.asig_a1.id])
        res = self.client.put(url, {'ambito': 'sede', 'local_id': self.sede_a.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_3_3_tecnico_cannot_perform_patch(self):
        """ATTACK: Tecnico forges PATCH on existing assignment to elevate self to responsable."""
        self.client.force_authenticate(self.tecnico_a)
        url = reverse('espacio-usuario-detail', args=[self.asig_a1.id])
        res = self.client.patch(url, {'tipo_responsabilidad': 'responsable'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_3_4_tecnico_cannot_perform_delete(self):
        """ATTACK: Tecnico forges DELETE on existing assignment."""
        self.client.force_authenticate(self.tecnico_a)
        url = reverse('espacio-usuario-detail', args=[self.asig_a1.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_3_5_docente_cannot_perform_post(self):
        """ATTACK: Docente forges POST to create an assignment."""
        self.client.force_authenticate(self.docente)
        payload = {
            'ambito': 'espacio',
            'espacio_id': self.espacio_a101.id,
            'usuario_id': self.docente.id,
            'tipo_responsabilidad': 'docente',
        }
        res = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_3_6_docente_cannot_perform_put(self):
        """ATTACK: Docente forges PUT on existing assignment."""
        self.client.force_authenticate(self.docente)
        url = reverse('espacio-usuario-detail', args=[self.asig_a1.id])
        res = self.client.put(url, {'tipo_responsabilidad': 'responsable'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_3_7_docente_cannot_perform_patch(self):
        """ATTACK: Docente forges PATCH on existing assignment."""
        self.client.force_authenticate(self.docente)
        url = reverse('espacio-usuario-detail', args=[self.asig_a1.id])
        res = self.client.patch(url, {'activo': False}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_3_8_docente_cannot_perform_delete(self):
        """ATTACK: Docente forges DELETE on existing assignment."""
        self.client.force_authenticate(self.docente)
        url = reverse('espacio-usuario-detail', args=[self.asig_a1.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_3_9_tecnico_and_docente_blocked_from_opciones_catalog(self):
        """ATTACK: Tecnico and Docente try to inspect administrative opciones catalog."""
        self.client.force_authenticate(self.tecnico_a)
        res_tec = self.client.get(self.opciones_url)
        self.assertEqual(res_tec.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.docente)
        res_doc = self.client.get(self.opciones_url)
        self.assertEqual(res_doc.status_code, status.HTTP_403_FORBIDDEN)

    # ══════════════════════════════════════════════════════════════════════════════
    # ATTACK VECTOR 4: Unauthenticated Access
    # ══════════════════════════════════════════════════════════════════════════════

    def test_4_1_unauthenticated_post_rejected(self):
        """ATTACK: Unauthenticated client attempts POST to create assignment."""
        self.client.logout()
        res = self.client.post(self.list_url, {'ambito': 'sede', 'local_id': self.sede_a.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_4_2_unauthenticated_put_rejected(self):
        """ATTACK: Unauthenticated client attempts PUT on assignment."""
        self.client.logout()
        url = reverse('espacio-usuario-detail', args=[self.asig_a1.id])
        res = self.client.put(url, {'ambito': 'sede', 'local_id': self.sede_a.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_4_3_unauthenticated_patch_rejected(self):
        """ATTACK: Unauthenticated client attempts PATCH on assignment."""
        self.client.logout()
        url = reverse('espacio-usuario-detail', args=[self.asig_a1.id])
        res = self.client.patch(url, {'tipo_responsabilidad': 'responsable'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_4_4_unauthenticated_delete_rejected(self):
        """ATTACK: Unauthenticated client attempts DELETE on assignment."""
        self.client.logout()
        url = reverse('espacio-usuario-detail', args=[self.asig_a1.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_4_5_unauthenticated_list_rejected(self):
        """ATTACK: Unauthenticated client attempts GET to list assignments."""
        self.client.logout()
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_4_6_unauthenticated_opciones_rejected(self):
        """ATTACK: Unauthenticated client attempts GET on opciones."""
        self.client.logout()
        res = self.client.get(self.opciones_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # ══════════════════════════════════════════════════════════════════════════════
    # ATTACK VECTOR 5: Multi-Sede Isolation, Role Matrix & Type Juggling
    # ══════════════════════════════════════════════════════════════════════════════

    def test_5_1_responsable_with_multiple_sedes_isolated_from_unassigned_sede(self):
        """ATTACK: Responsable assigned to Sede A and Sede C can manage A and C, but strictly blocked in Sede B."""
        sede_c = Local.objects.create(codigo='LOC-SEDE-C-IT2', nombre='Sede C Pucallpa', tipo='sede')
        edificio_c1 = Edificio.objects.create(codigo='EDIF-C1-IT2', nombre='Pabellón C1', local=sede_c)
        UsuarioSede.objects.create(usuario=self.responsable_a, local=sede_c, activo=True)

        self.client.force_authenticate(self.responsable_a)

        # Authorized creation in Sede C (new assignment)
        res_c = self.client.post(self.list_url, {
            'ambito': 'edificio',
            'edificio_id': edificio_c1.id,
            'usuario_id': self.tecnico_a.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_c.status_code, status.HTTP_201_CREATED)

        # Strictly blocked in foreign Sede B
        res_b = self.client.post(self.list_url, {
            'ambito': 'edificio',
            'edificio_id': self.edificio_b1.id,
            'usuario_id': self.tecnico_a.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        self.assertEqual(res_b.status_code, status.HTTP_403_FORBIDDEN)

    def test_5_2_rol_usuario_blocked_from_all_read_and_write(self):
        """ATTACK: Basic authenticated user ('usuario') has no access to any read or write operation."""
        self.client.force_authenticate(self.usuario_comun)

        res_get = self.client.get(self.list_url)
        self.assertEqual(res_get.status_code, status.HTTP_403_FORBIDDEN)

        res_post = self.client.post(self.list_url, {'ambito': 'sede', 'local_id': self.sede_a.id}, format='json')
        self.assertEqual(res_post.status_code, status.HTTP_403_FORBIDDEN)

        url_detail = reverse('espacio-usuario-detail', args=[self.asig_a1.id])
        res_put = self.client.put(url_detail, {'ambito': 'sede', 'local_id': self.sede_a.id}, format='json')
        self.assertEqual(res_put.status_code, status.HTTP_403_FORBIDDEN)

        res_patch = self.client.patch(url_detail, {'activo': False}, format='json')
        self.assertEqual(res_patch.status_code, status.HTTP_403_FORBIDDEN)

        res_del = self.client.delete(url_detail)
        self.assertEqual(res_del.status_code, status.HTTP_403_FORBIDDEN)

        res_opc = self.client.get(self.opciones_url)
        self.assertEqual(res_opc.status_code, status.HTTP_403_FORBIDDEN)

    def test_5_3_malformed_type_juggling_rejected(self):
        """ATTACK: Type juggling with non-integer strings, objects, lists, whitespace and overflow does not bypass validation."""
        self.client.force_authenticate(self.responsable_a)

        # 1. Malformed local_id (SQL-like string / text in integer FK)
        res_malformed_local = self.client.post(
            self.list_url,
            {
                'ambito': 'sede',
                'local_id': "1 OR 1=1",
                'usuario_id': self.tecnico_a.id,
            },
            format='json',
        )
        self.assertEqual(res_malformed_local.status_code, status.HTTP_400_BAD_REQUEST)

        # 2. Malformed piso: Object/dictionary injection
        res_dict_piso = self.client.post(
            self.list_url,
            {
                'ambito': 'piso',
                'edificio_id': self.edificio_a1.id,
                'piso': {'evil': 'payload'},
                'usuario_id': self.tecnico_a.id,
            },
            format='json',
        )
        self.assertEqual(res_dict_piso.status_code, status.HTTP_400_BAD_REQUEST)

        # 3. Malformed piso: Array/list injection
        res_list_piso = self.client.post(
            self.list_url,
            {
                'ambito': 'piso',
                'edificio_id': self.edificio_a1.id,
                'piso': ['1', '2'],
                'usuario_id': self.tecnico_a.id,
            },
            format='json',
        )
        self.assertEqual(res_list_piso.status_code, status.HTTP_400_BAD_REQUEST)

        # 4. Malformed piso: Empty / whitespace-only string
        res_space_piso = self.client.post(
            self.list_url,
            {
                'ambito': 'piso',
                'edificio_id': self.edificio_a1.id,
                'piso': '   ',
                'usuario_id': self.tecnico_a.id,
            },
            format='json',
        )
        self.assertEqual(res_space_piso.status_code, status.HTTP_400_BAD_REQUEST)

        # 5. Malformed piso: Exceeds max length of 20 characters
        res_overflow_piso = self.client.post(
            self.list_url,
            {
                'ambito': 'piso',
                'edificio_id': self.edificio_a1.id,
                'piso': 'P' * 25,
                'usuario_id': self.tecnico_a.id,
            },
            format='json',
        )
        self.assertEqual(res_overflow_piso.status_code, status.HTTP_400_BAD_REQUEST)

    def test_5_4_invalid_or_escalated_tipo_responsabilidad_rejected(self):
        """ATTACK: Passing forged or unauthorized tipo_responsabilidad (e.g. 'superadmin') is rejected."""
        self.client.force_authenticate(self.responsable_a)

        res = self.client.post(
            self.list_url,
            {
                'ambito': 'edificio',
                'edificio_id': self.edificio_a1.id,
                'usuario_id': self.tecnico_a.id,
                'tipo_responsabilidad': 'superadmin',
            },
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tipo_responsabilidad', str(res.data))

    # ══════════════════════════════════════════════════════════════════════════════
    # ATTACK VECTOR 6: MANDATED VERIFICATION REQUIREMENTS 2 & 3
    # ══════════════════════════════════════════════════════════════════════════════

    def test_6_1_operator_with_zero_active_sedes_gets_empty_list_and_no_leakage(self):
        """
        REQUIREMENT 2: Verify that an operator with 0 active sedes querying
        GET /api/v1/espacios/usuarios/ gets an empty list ([]) and cannot see assignments in any sede.
        """
        # Ensure active assignments exist in both Sede A and Sede B
        self.assertTrue(EspacioUsuario.objects.filter(local=self.sede_a, activo=True).exists())
        self.assertTrue(EspacioUsuario.objects.filter(local=self.sede_b, activo=True).exists())

        # 1. Tecnico with 0 sedes in UsuarioSede
        tecnico_sin_sede = Usuario.objects.create_user(
            username='tec.zero.sedes',
            correo='tec.zero.sedes@udh.edu.pe',
            rol='tecnico',
        )
        self.client.force_authenticate(tecnico_sin_sede)
        res_tec = self.client.get(self.list_url)
        self.assertEqual(res_tec.status_code, status.HTTP_200_OK)
        tec_data = res_tec.data.get('results', res_tec.data) if isinstance(res_tec.data, dict) else res_tec.data
        self.assertEqual(tec_data, [], "Operator with 0 sedes received non-empty assignments list!")

        # 2. Responsable with 0 active sedes in UsuarioSede
        responsable_sin_sede = Usuario.objects.create_user(
            username='resp.zero.sedes',
            correo='resp.zero.sedes@udh.edu.pe',
            rol='responsable',
        )
        self.client.force_authenticate(responsable_sin_sede)
        res_resp = self.client.get(self.list_url)
        self.assertEqual(res_resp.status_code, status.HTTP_200_OK)
        resp_data = res_resp.data.get('results', res_resp.data) if isinstance(res_resp.data, dict) else res_resp.data
        self.assertEqual(resp_data, [], "Responsable with 0 sedes received non-empty assignments list!")

        # 3. Docente with 0 active sedes in UsuarioSede
        docente_sin_sede = Usuario.objects.create_user(
            username='doc.zero.sedes',
            correo='doc.zero.sedes@udh.edu.pe',
            rol='docente',
        )
        self.client.force_authenticate(docente_sin_sede)
        res_doc = self.client.get(self.list_url)
        self.assertEqual(res_doc.status_code, status.HTTP_200_OK)
        doc_data = res_doc.data.get('results', res_doc.data) if isinstance(res_doc.data, dict) else res_doc.data
        self.assertEqual(doc_data, [], "Docente with 0 sedes received non-empty assignments list!")

    def test_6_2_responsable_opciones_filtered_to_assigned_sedes(self):
        """
        REQUIREMENT 3: Verify that responsable accessing GET /api/v1/espacios/usuarios/opciones/
        receives HTTP 200 with options strictly filtered to their assigned physical sedes.
        """
        self.client.force_authenticate(self.responsable_a)
        res = self.client.get(self.opciones_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.data
        self.assertIn('locales', data)
        self.assertIn('edificios', data)
        self.assertIn('espacios', data)

        # Verify locales only contain Sede A, strictly excluding Sede B
        returned_local_ids = [item['id'] for item in data['locales']]
        self.assertIn(self.sede_a.id, returned_local_ids, "Assigned Sede A missing from locales!")
        self.assertNotIn(self.sede_b.id, returned_local_ids, "Foreign Sede B leaked into locales!")

        # Verify edificios only contain Sede A buildings, strictly excluding Sede B buildings
        returned_edif_local_ids = {item['local_id'] for item in data['edificios']}
        self.assertIn(self.sede_a.id, returned_edif_local_ids)
        self.assertNotIn(self.sede_b.id, returned_edif_local_ids, "Foreign building from Sede B leaked!")

        # Verify edificios list contains Edificio A1 and does not contain Edificio B1
        returned_edif_ids = [item['id'] for item in data['edificios']]
        self.assertIn(self.edificio_a1.id, returned_edif_ids)
        self.assertNotIn(self.edificio_b1.id, returned_edif_ids, "Foreign edificio B1 leaked into opciones!")


def run_adversarial_suite():
    """Runs the test suite using Django's DiscoverRunner."""
    from django.test.runner import DiscoverRunner
    runner = DiscoverRunner(verbosity=2, interactive=False)
    suite = unittest.TestSuite()
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(AdversarialSecurityM1Iter2Tests)
    suite.addTests(tests)

    old_config = runner.setup_databases()
    runner.setup_test_environment()
    try:
        result = runner.run_suite(suite)
        print("\n" + "=" * 70)
        print("ADVERSARIAL SECURITY VERIFICATION SUMMARY (ITERATION 2):")
        print(f"Total attacks & requirements tested: {result.testsRun}")
        print(f"Bypasses / Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print("=" * 70)
        if result.wasSuccessful():
            print("VERDICT: ALL SECURITY BOUNDARIES HELD. ATTACKS REPELLED. REQUIREMENTS SATISFIED.")
            return True
        else:
            print("VERDICT: SECURITY BREACH DETECTED. ATTACK SUCCEEDED.")
            return False
    finally:
        runner.teardown_test_environment()
        runner.teardown_databases(old_config)


if __name__ == '__main__':
    success = run_adversarial_suite()
    sys.exit(0 if success else 1)
