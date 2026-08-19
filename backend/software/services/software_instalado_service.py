from datetime import date

from django.db import transaction
from rest_framework.exceptions import ValidationError

from shared.base import BaseService
from shared.mixins import AuditableMixin
from software.models import SoftwareInstalado
from software.repositories import SoftwareInstaladoRepository
from usuarios.models import Usuario


class SoftwareInstaladoService(AuditableMixin, BaseService):
    """Gestiona la asignacion y el retiro de software en los equipos."""

    SOFTWARE_INSTALADO = 'equipo.software_instalado'
    SOFTWARE_RETIRADO = 'equipo.software_retirado'

    def __init__(self):
        self.repository = SoftwareInstaladoRepository()

    def listar(self, equipo_id: int | None = None):
        """Retorna instalaciones vigentes filtradas opcionalmente por equipo."""
        return self.repository.listar(equipo_id=equipo_id)

    @transaction.atomic
    def _do_create(self, data: dict, actor: Usuario = None):
        clean_data = data.copy()
        equipo = self._resolver_equipo(clean_data.pop('equipo_id'))
        producto = self._resolver_producto(
            clean_data.pop('producto_software_id'),
        )
        existente = self.repository.get_by_equipo_producto_including_deleted(
            equipo.id,
            producto.id,
        )

        if existente is not None and not existente.is_deleted:
            raise ValidationError({
                'producto_software_id': (
                    'Este software ya se encuentra instalado en el equipo.'
                ),
            })

        self._validar_licencia_disponible(producto)
        self._validar_fecha_instalacion(clean_data['fecha_instalacion'])
        numero_licencia = clean_data.get('numero_licencia_usado', '').strip()

        if existente is not None:
            instance = self.repository.restore(
                existente,
                numero_licencia_usado=numero_licencia,
                fecha_instalacion=clean_data['fecha_instalacion'],
                actor=actor,
            )
        else:
            instance = self.repository.create(
                equipo=equipo,
                producto_software=producto,
                numero_licencia_usado=numero_licencia,
                fecha_instalacion=clean_data['fecha_instalacion'],
                created_by=actor,
                updated_by=actor,
            )

        return self.repository.get_by_id(instance.id), {
            'equipo': equipo,
            'producto': producto,
        }

    def _do_delete(self, id: int, actor: Usuario = None) -> SoftwareInstalado:
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)
        return instance

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        equipo = ctx['equipo']
        producto = ctx['producto']
        self._audit_registrar(
            equipo,
            self.SOFTWARE_INSTALADO,
            actor,
            f'{producto.software} {producto.version} instalado en {equipo.codigo}.',
            datos_extra={
                'instalacion_id': instance.id,
                'producto_software_id': producto.id,
            },
        )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(
            instance.equipo,
            self.SOFTWARE_RETIRADO,
            actor,
            (
                f'{instance.producto_software.software} '
                f'{instance.producto_software.version} retirado de '
                f'{instance.equipo.codigo}.'
            ),
            datos_extra={
                'instalacion_id': instance.id,
                'producto_software_id': instance.producto_software_id,
            },
        )

    def _resolver_equipo(self, equipo_id: int):
        equipo = self.repository.get_equipo_by_id(equipo_id)
        if equipo is None:
            raise ValidationError({
                'equipo_id': 'El equipo no existe o fue dado de baja.',
            })
        return equipo

    def _resolver_producto(self, producto_id: int):
        producto = self.repository.get_producto_by_id_for_update(producto_id)
        if producto is None:
            raise ValidationError({
                'producto_software_id': (
                    'El producto de software no existe o fue retirado.'
                ),
            })
        return producto

    def _validar_licencia_disponible(self, producto) -> None:
        """Impide asignar productos sin licencias vigentes disponibles."""
        if producto.fecha_expiracion and producto.fecha_expiracion < date.today():
            raise ValidationError({
                'producto_software_id': 'La licencia del producto ha expirado.',
            })

        if producto.tipo_licencia == 'libre':
            return

        usadas = self.repository.count_active_by_producto(producto.id)
        if usadas >= producto.licencias_totales:
            raise ValidationError({
                'producto_software_id': (
                    'No hay licencias disponibles para este producto.'
                ),
            })

    @staticmethod
    def _validar_fecha_instalacion(fecha_instalacion) -> None:
        """Evita registrar como realizada una instalacion con fecha futura."""
        if fecha_instalacion > date.today():
            raise ValidationError({
                'fecha_instalacion': (
                    'La fecha de instalacion no puede estar en el futuro.'
                ),
            })
