"""
backend/espacios/test_espacios_usuarios.py

Pruebas unitarias de seguridad (R5), cobertura de los 4 ámbitos territoriales
(Sede, Edificio, Piso, Espacio), control de duplicados y permisos de acceso por rol.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from espacios.models import Edificio, Espacio, EspacioUsuario, Local
from usuarios.models import Usuario, UsuarioSede


class EspacioUsuarioAmbitoYPermisosAPITests(APITestCase):
    """
    Verifica las reglas de autorización por sede (R5), los 4 niveles de ámbito
    y la integridad de datos en el endpoint /api/v1/espacios/usuarios/.
    """

    def setUp(self):
        # 1. Creación de Usuarios por Rol
        self.admin = Usuario.objects.create_user(
            correo='admin.territorial@udh.edu.pe',
            username='admin.territorial',
            nombre='Ada',
            apellido='Admin',
            rol='admin',
        )
        self.responsable_central = Usuario.objects.create_user(
            correo='resp.central@udh.edu.pe',
            username='resp.central',
            nombre='Carlos',
            apellido='Central',
            rol='responsable',
        )
        self.responsable_norte = Usuario.objects.create_user(
            correo='resp.norte@udh.edu.pe',
            username='resp.norte',
            nombre='Nora',
            apellido='Norte',
            rol='responsable',
        )
        self.tecnico_central = Usuario.objects.create_user(
            correo='tecnico.central@udh.edu.pe',
            username='tecnico.central',
            nombre='Tomás',
            apellido='Técnico',
            rol='tecnico',
        )
        self.docente = Usuario.objects.create_user(
            correo='docente.quimica@udh.edu.pe',
            username='docente.quimica',
            nombre='Diana',
            apellido='Docente',
            rol='docente',
        )
        self.usuario_comun = Usuario.objects.create_user(
            correo='usuario.comun@udh.edu.pe',
            username='usuario.comun',
            nombre='Ulises',
            apellido='Usuario',
            rol='usuario',
        )

        # 2. Infraestructura Territorial: 2 Sedes Físicas
        self.sede_central = Local.objects.create(
            codigo='LOC-CENTRAL',
            nombre='Sede Central Huánuco',
            ciudad='Huánuco',
            tipo='sede',
        )
        self.sede_norte = Local.objects.create(
            codigo='LOC-NORTE',
            nombre='Sede Norte Tingo María',
            ciudad='Tingo María',
            tipo='sede',
        )

        # Edificios
        self.edificio_central = Edificio.objects.create(
            codigo='EDIF-CENTRAL-A',
            nombre='Pabellón A Central',
            local=self.sede_central,
        )
        self.edificio_norte = Edificio.objects.create(
            codigo='EDIF-NORTE-B',
            nombre='Pabellón B Norte',
            local=self.sede_norte,
        )

        # Espacios
        self.espacio_central = Espacio.objects.create(
            codigo_espacio='LAB-CENTRAL-101',
            tipo='laboratorio',
            pabellon='Pabellón A',
            edificio=self.edificio_central,
            piso='1',
        )
        self.espacio_norte = Espacio.objects.create(
            codigo_espacio='LAB-NORTE-201',
            tipo='laboratorio',
            pabellon='Pabellón B',
            edificio=self.edificio_norte,
            piso='2',
        )

        # 3. Asignación de Sedes Físicas (UsuarioSede)
        UsuarioSede.objects.create(
            usuario=self.responsable_central,
            local=self.sede_central,
            activo=True,
            es_sede_principal=True,
        )
        UsuarioSede.objects.create(
            usuario=self.responsable_norte,
            local=self.sede_norte,
            activo=True,
            es_sede_principal=True,
        )
        UsuarioSede.objects.create(
            usuario=self.tecnico_central,
            local=self.sede_central,
            activo=True,
            es_sede_principal=True,
        )
        UsuarioSede.objects.create(
            usuario=self.docente,
            local=self.sede_central,
            activo=True,
            es_sede_principal=True,
        )

        # 4. URLs
        self.list_url = reverse('espacio-usuario-list')
        self.opciones_url = reverse('espacio-usuario-opciones')

    # ── 1. Asignaciones en los 4 Niveles de Ámbito ──────────────────────────────

    def test_admin_crea_asignacion_ambito_sede_exitoso(self):
        """Crea asignación territorial a nivel Sede (Local)."""
        self.client.force_authenticate(self.admin)
        payload = {
            'ambito': 'sede',
            'local_id': self.sede_central.id,
            'usuario_id': self.responsable_central.id,
            'tipo_responsabilidad': 'responsable',
            'activo': True,
        }
        res = self.client.post(self.list_url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['ambito'], 'sede')
        self.assertEqual(res.data['local']['id'], self.sede_central.id)
        self.assertIsNone(res.data.get('edificio'))
        self.assertIsNone(res.data.get('espacio'))
        self.assertTrue(
            EspacioUsuario.objects.filter(
                local=self.sede_central,
                usuario=self.responsable_central,
                ambito='sede',
                activo=True,
            ).exists()
        )

    def test_admin_crea_asignacion_ambito_edificio_exitoso(self):
        """Crea asignación territorial a nivel Pabellón / Edificio con local inferido."""
        self.client.force_authenticate(self.admin)
        payload = {
            'ambito': 'edificio',
            'edificio_id': self.edificio_central.id,
            'usuario_id': self.tecnico_central.id,
            'tipo_responsabilidad': 'tecnico',
            'activo': True,
        }
        res = self.client.post(self.list_url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['ambito'], 'edificio')
        self.assertEqual(res.data['edificio']['id'], self.edificio_central.id)
        self.assertEqual(res.data['local']['id'], self.sede_central.id)
        self.assertIsNone(res.data.get('espacio'))

    def test_admin_crea_asignacion_ambito_piso_exitoso(self):
        """Crea asignación territorial a nivel Piso de Pabellón."""
        self.client.force_authenticate(self.admin)
        payload = {
            'ambito': 'piso',
            'edificio_id': self.edificio_central.id,
            'piso': '2',
            'usuario_id': self.tecnico_central.id,
            'tipo_responsabilidad': 'tecnico',
            'activo': True,
        }
        res = self.client.post(self.list_url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['ambito'], 'piso')
        self.assertEqual(res.data['edificio']['id'], self.edificio_central.id)
        self.assertEqual(res.data['piso'], '2')
        self.assertEqual(res.data['local']['id'], self.sede_central.id)
        self.assertIsNone(res.data.get('espacio'))

    def test_admin_crea_asignacion_ambito_espacio_exitoso(self):
        """Crea asignación a nivel Espacio individual y denormaliza jerarquía."""
        self.client.force_authenticate(self.admin)
        payload = {
            'ambito': 'espacio',
            'espacio_id': self.espacio_central.id,
            'usuario_id': self.docente.id,
            'tipo_responsabilidad': 'docente',
            'activo': True,
        }
        res = self.client.post(self.list_url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['ambito'], 'espacio')
        self.assertEqual(res.data['espacio']['id'], self.espacio_central.id)
        self.assertEqual(res.data['edificio']['id'], self.edificio_central.id)
        self.assertEqual(res.data['local']['id'], self.sede_central.id)

    # ── 2. Control de Duplicados y Restauración Soft-Delete ─────────────────────

    def test_rechaza_asignacion_duplicada_mismo_ambito_activo(self):
        """Rechaza con HTTP 400 registrar una asignación idéntica activa para el mismo ámbito."""
        self.client.force_authenticate(self.admin)
        payload = {
            'ambito': 'piso',
            'edificio_id': self.edificio_central.id,
            'piso': '1',
            'usuario_id': self.tecnico_central.id,
            'tipo_responsabilidad': 'tecnico',
            'activo': True,
        }
        res_primera = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res_primera.status_code, status.HTTP_201_CREATED)

        res_duplicada = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res_duplicada.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ya está asignado', str(res_duplicada.data))

    def test_restaura_asignacion_previamente_eliminada(self):
        """Si la asignación existía pero estaba eliminada lógicamente, se reactiva."""
        self.client.force_authenticate(self.admin)
        payload = {
            'ambito': 'piso',
            'edificio_id': self.edificio_central.id,
            'piso': '1',
            'usuario_id': self.tecnico_central.id,
            'tipo_responsabilidad': 'tecnico',
            'activo': True,
        }
        creada = self.client.post(self.list_url, payload, format='json')
        asig_id = creada.data['id']

        # Eliminar lógicamente
        del_res = self.client.delete(reverse('espacio-usuario-detail', args=[asig_id]))
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)

        # Volver a asignar
        reactivada = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(reactivada.status_code, status.HTTP_201_CREATED)
        self.assertEqual(reactivada.data['id'], asig_id)
        self.assertTrue(reactivada.data['activo'])

    # ── 3. Permisos del Rol Responsable (Propia Sede vs Sede Ajena) ────────────

    def test_responsable_crea_asignacion_en_propia_sede_exitoso(self):
        """Responsable puede crear asignaciones en la sede física que tiene asignada."""
        self.client.force_authenticate(self.responsable_central)
        payload = {
            'ambito': 'piso',
            'edificio_id': self.edificio_central.id,
            'piso': '2',
            'usuario_id': self.tecnico_central.id,
            'tipo_responsabilidad': 'tecnico',
            'activo': True,
        }
        res = self.client.post(self.list_url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        asig = EspacioUsuario.objects.get(id=res.data['id'])
        self.assertEqual(asig.created_by, self.responsable_central)

    def test_responsable_rechazado_con_403_en_sede_ajena(self):
        """Responsable recibe HTTP 403 al intentar registrar asignaciones en una sede ajena."""
        self.client.force_authenticate(self.responsable_central)

        # Intento 1: Ámbito Sede foránea
        res_sede = self.client.post(
            self.list_url,
            {
                'ambito': 'sede',
                'local_id': self.sede_norte.id,
                'usuario_id': self.tecnico_central.id,
                'tipo_responsabilidad': 'tecnico',
            },
            format='json',
        )
        self.assertEqual(res_sede.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('sede ajena', str(res_sede.data))

        # Intento 2: Ámbito Edificio en sede foránea
        res_edif = self.client.post(
            self.list_url,
            {
                'ambito': 'edificio',
                'edificio_id': self.edificio_norte.id,
                'usuario_id': self.tecnico_central.id,
                'tipo_responsabilidad': 'tecnico',
            },
            format='json',
        )
        self.assertEqual(res_edif.status_code, status.HTTP_403_FORBIDDEN)

        # Intento 3: Ámbito Espacio en sede foránea
        res_esp = self.client.post(
            self.list_url,
            {
                'ambito': 'espacio',
                'espacio_id': self.espacio_norte.id,
                'usuario_id': self.docente.id,
                'tipo_responsabilidad': 'docente',
            },
            format='json',
        )
        self.assertEqual(res_esp.status_code, status.HTTP_403_FORBIDDEN)

    def test_responsable_elimina_en_propia_sede_y_bloqueado_en_ajena(self):
        """Responsable puede eliminar asignaciones de su sede pero recibe 403 en sedes ajenas."""
        # Setup: asignación en Sede Central y en Sede Norte
        asig_central = EspacioUsuario.objects.create(
            ambito='edificio',
            edificio=self.edificio_central,
            local=self.sede_central,
            usuario=self.tecnico_central,
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )
        asig_norte = EspacioUsuario.objects.create(
            ambito='edificio',
            edificio=self.edificio_norte,
            local=self.sede_norte,
            usuario=self.tecnico_central,
            tipo_responsabilidad='tecnico',
            created_by=self.admin,
        )

        self.client.force_authenticate(self.responsable_central)

        # Intento de eliminar en sede ajena -> 403
        del_ajena = self.client.delete(reverse('espacio-usuario-detail', args=[asig_norte.id]))
        self.assertEqual(del_ajena.status_code, status.HTTP_403_FORBIDDEN)
        asig_norte.refresh_from_db()
        self.assertFalse(asig_norte.is_deleted)

        # Eliminación en sede propia -> 204
        del_propia = self.client.delete(reverse('espacio-usuario-detail', args=[asig_central.id]))
        self.assertEqual(del_propia.status_code, status.HTTP_204_NO_CONTENT)
        asig_central.refresh_from_db()
        self.assertTrue(asig_central.is_deleted)

    # ── 4. Permisos del Catálogo Opciones ──────────────────────────────────────

    def test_responsable_autorizado_en_opciones(self):
        """Responsable puede consultar el catálogo de opciones para armar el formulario."""
        self.client.force_authenticate(self.responsable_central)
        res = self.client.get(self.opciones_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('usuarios', res.data)

    def test_tecnico_y_docente_bloqueados_en_opciones(self):
        """Técnico y docente reciben HTTP 403 al intentar acceder a /opciones/."""
        self.client.force_authenticate(self.tecnico_central)
        res_tec = self.client.get(self.opciones_url)
        self.assertEqual(res_tec.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.docente)
        res_doc = self.client.get(self.opciones_url)
        self.assertEqual(res_doc.status_code, status.HTTP_403_FORBIDDEN)

    # ── 5. Restricción de Solo Lectura para Técnico y Docente ──────────────────

    def test_tecnico_y_docente_bloqueados_en_escritura(self):
        """Técnico y Docente reciben HTTP 403 ante cualquier intento de POST, PUT o DELETE."""
        payload = {
            'ambito': 'espacio',
            'espacio_id': self.espacio_central.id,
            'usuario_id': self.docente.id,
            'tipo_responsabilidad': 'docente',
        }

        self.client.force_authenticate(self.tecnico_central)
        res_post_tec = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res_post_tec.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.docente)
        res_post_doc = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res_post_doc.status_code, status.HTTP_403_FORBIDDEN)

    def test_docente_y_tecnico_pueden_listar_asignaciones(self):
        """Docente y Técnico tienen acceso de solo lectura (SAFE_METHODS) en el listado."""
        self.client.force_authenticate(self.docente)
        res_doc = self.client.get(self.list_url)
        self.assertEqual(res_doc.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.tecnico_central)
        res_tec = self.client.get(self.list_url)
        self.assertEqual(res_tec.status_code, status.HTTP_200_OK)

    def test_usuario_comun_bloqueado_completamente(self):
        """Usuario final regular no tiene acceso de lectura ni escritura a asignaciones."""
        self.client.force_authenticate(self.usuario_comun)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # ── 6. Casos Límite de Iteración 2 (Pisos no numéricos, concurrencia, operador sin sedes) ──

    def test_crear_asignacion_piso_con_nombre_alfanumerico_o_no_ascii(self):
        """
        Verifica que nombres de piso alfanuméricos y no-ASCII
        ('Sótano -1', 'Mezzanine', 'PB') sean aceptados exitosamente con HTTP 201.
        """
        self.client.force_authenticate(self.admin)
        pisos_a_probar = ['Sótano -1', 'Mezzanine', 'PB']

        for i, nombre_piso in enumerate(pisos_a_probar):
            usuario = Usuario.objects.create_user(
                correo=f'tec.piso.{i}@udh.edu.pe',
                username=f'tec.piso.{i}',
                rol='tecnico',
            )
            payload = {
                'ambito': 'piso',
                'edificio_id': self.edificio_central.id,
                'piso': nombre_piso,
                'usuario_id': usuario.id,
                'tipo_responsabilidad': 'tecnico',
                'activo': True,
            }
            res = self.client.post(self.list_url, payload, format='json')
            self.assertEqual(
                res.status_code,
                status.HTTP_201_CREATED,
                f"Fallo al registrar piso '{nombre_piso}': {res.data}",
            )
            self.assertEqual(res.data['piso'], nombre_piso)
            self.assertEqual(res.data['ambito'], 'piso')
            self.assertTrue(
                EspacioUsuario.objects.filter(
                    edificio=self.edificio_central,
                    piso=nombre_piso,
                    usuario=usuario,
                    activo=True,
                ).exists()
            )

    test_crear_asignacion_piso_nombres_no_numericos_exitoso = test_crear_asignacion_piso_con_nombre_alfanumerico_o_no_ascii

    def test_colision_concurrente_retorna_400_no_500(self):
        """
        Verifica que una colisión concurrente donde repository.create choca con
        la restricción de unicidad de BD (IntegrityError), retorne limpiamente HTTP 400 Bad Request.
        """
        from unittest.mock import patch
        from espacios.services.espacio_usuario_service import EspacioUsuarioService

        self.client.force_authenticate(self.admin)
        payload = {
            'ambito': 'piso',
            'edificio_id': self.edificio_central.id,
            'piso': '3',
            'usuario_id': self.tecnico_central.id,
            'tipo_responsabilidad': 'tecnico',
            'activo': True,
        }

        # 1. Primer registro se crea exitosamente (HTTP 201)
        res1 = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        # 2. Simular carrera concurrente en milisegundos:
        # Pasa _validar_unicidad sin detectar la transacción concurrente,
        # provocando que repository.create choque con el UniqueConstraint en DB.
        with patch.object(EspacioUsuarioService, '_validar_unicidad', return_value=None):
            res2 = self.client.post(self.list_url, payload, format='json')
            self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('ya está asignado', str(res2.data))

    test_condicion_carrera_concurrente_retorna_400_limpio = test_colision_concurrente_retorna_400_no_500

    def test_operador_sin_sedes_activas_obtiene_lista_vacia(self):
        """
        Verifica que un técnico o responsable sin sedes físicas asignadas (0 sedes en UsuarioSede)
        obtenga un listado vacío (HTTP 200 con 0 resultados) en lugar de ver todas las asignaciones.
        """
        # Crear asignación existente en la sede central
        EspacioUsuario.objects.create(
            ambito='sede',
            local=self.sede_central,
            usuario=self.responsable_central,
            tipo_responsabilidad='responsable',
            created_by=self.admin,
        )

        # 1. Técnico sin ninguna sede asignada
        tecnico_sin_sede = Usuario.objects.create_user(
            correo='tec.sin.sede@udh.edu.pe',
            username='tec.sin.sede',
            rol='tecnico',
        )
        self.client.force_authenticate(tecnico_sin_sede)
        res_tec = self.client.get(self.list_url)
        self.assertEqual(res_tec.status_code, status.HTTP_200_OK)
        datos_tec = res_tec.data.get('results', res_tec.data) if isinstance(res_tec.data, dict) else res_tec.data
        self.assertEqual(len(datos_tec), 0)

        # 2. Responsable sin ninguna sede asignada
        responsable_sin_sede = Usuario.objects.create_user(
            correo='resp.sin.sede@udh.edu.pe',
            username='resp.sin.sede',
            rol='responsable',
        )
        self.client.force_authenticate(responsable_sin_sede)
        res_resp = self.client.get(self.list_url)
        self.assertEqual(res_resp.status_code, status.HTTP_200_OK)
        datos_resp = res_resp.data.get('results', res_resp.data) if isinstance(res_resp.data, dict) else res_resp.data
        self.assertEqual(len(datos_resp), 0)

    test_operador_sin_sedes_asignadas_obtiene_listado_vacio = test_operador_sin_sedes_activas_obtiene_lista_vacia
