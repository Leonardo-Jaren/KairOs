from datetime import date

from django.urls import reverse
from rest_framework.test import APITestCase

from equipos.models import Componente, Equipo
from equipos.serializers import EquipoCreateUpdateSerializer
from usuarios.models import Usuario


class ComponenteAPITests(APITestCase):
    """Verifica filtros y paginacion del listado global de componentes."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin-componentes@example.com',
            username='admin_componentes',
            nombre='Ada',
            password='AdminPass123',
            rol='admin',
        )
        self.equipo = Equipo.objects.create(
            codigo='LAB201-PC040',
            numero_serie='SERIE-COMP-040',
            tipo_equipo='desktop',
            marca='Lenovo',
            modelo='ThinkCentre',
            modo_adquisicion='comprado',
            fecha_adquisicion=date(2026, 1, 10),
        )
        self.cpu = Componente.objects.create(
            equipo=self.equipo,
            tipo='cpu',
            modelo='Intel Core i5-12400',
            descripcion='6 nucleos, hasta 4.4 GHz',
        )
        self.ram = Componente.objects.create(
            equipo=self.equipo,
            tipo='ram',
            modelo='Kingston Fury',
            descripcion='16 GB DDR4',
        )
        self.url = reverse('componente-list')
        self.client.force_authenticate(self.admin)

    def test_filtra_componentes_por_tipo(self):
        """Retorna solo el tipo solicitado antes de aplicar la paginacion."""
        response = self.client.get(self.url, {'tipo': 'ram'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.ram.id)

    def test_busca_componentes_en_todas_las_paginas(self):
        """Busca por modelo o equipo sobre el conjunto completo."""
        response = self.client.get(self.url, {'search': 'i5-12400'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.cpu.id)


class EquipoIPSerializerTests(APITestCase):
    """Verifica la obligatoriedad y el formato de las direcciones IP."""

    def datos_base(self):
        return {
            'codigo': 'LAB-IP-PC001',
            'numero_serie': 'SERIE-IP-001',
            'tipo_equipo': 'desktop',
            'marca': 'Lenovo',
            'modelo': 'ThinkCentre',
            'modo_adquisicion': 'comprado',
            'fecha_adquisicion': '2026-01-10',
            'estado': 'en_uso',
        }

    def test_ipv4_es_obligatoria(self):
        serializer = EquipoCreateUpdateSerializer(data=self.datos_base())

        self.assertFalse(serializer.is_valid())
        self.assertIn('ipv4', serializer.errors)

    def test_rechaza_ipv4_invalida(self):
        datos = self.datos_base() | {'ipv4': '192.168.1.300'}
        serializer = EquipoCreateUpdateSerializer(data=datos)

        self.assertFalse(serializer.is_valid())
        self.assertIn('ipv4', serializer.errors)

    def test_acepta_ipv4_y_ipv6_opcional(self):
        datos = self.datos_base() | {'ipv4': '192.168.1.10'}
        serializer = EquipoCreateUpdateSerializer(data=datos)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rechaza_ipv6_invalida(self):
        datos = self.datos_base() | {'ipv4': '192.168.1.10', 'ipv6': '2001:db8:::10'}
        serializer = EquipoCreateUpdateSerializer(data=datos)

        self.assertFalse(serializer.is_valid())
        self.assertIn('ipv6', serializer.errors)
