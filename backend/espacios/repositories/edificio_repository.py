from django.db import transaction
from django.db.models import Count, Q

from espacios.models import Edificio, Espacio
from shared.base import BaseRepository
from usuarios.models import Usuario


class EdificioRepository(BaseRepository):
    """Centraliza consultas y persistencia de los edificios del campus."""

    model = Edificio

    def get_all(self):
        """Retorna edificios vigentes con contadores de sus espacios."""
        return self.model.objects.filter(is_deleted=False).select_related(
            'local',
        ).annotate(
            cantidad_espacios=Count(
                'espacios',
                filter=Q(espacios__is_deleted=False),
                distinct=True,
            ),
            cantidad_pisos=Count(
                'espacios__piso',
                filter=Q(espacios__is_deleted=False),
                distinct=True,
            ),
            cantidad_laboratorios=Count(
                'espacios',
                filter=Q(
                    espacios__is_deleted=False,
                    espacios__tipo='laboratorio',
                ),
                distinct=True,
            ),
            cantidad_aulas=Count(
                'espacios',
                filter=Q(
                    espacios__is_deleted=False,
                    espacios__tipo='aula',
                ),
                distinct=True,
            ),
        ).order_by('nombre', 'codigo')

    def get_by_id(self, id: int) -> Edificio | None:
        """Busca un edificio vigente por identificador."""
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(
        self,
        busqueda: str = '',
        activo: bool | None = None,
        local_id: int | None = None,
    ):
        """Aplica búsqueda por código, nombre o descripción y estado."""
        queryset = self.get_all()
        if busqueda:
            queryset = queryset.filter(
                Q(codigo__icontains=busqueda)
                | Q(nombre__icontains=busqueda)
                | Q(descripcion__icontains=busqueda)
            )
        if activo is not None:
            queryset = queryset.filter(activo=activo)
        if local_id is not None:
            queryset = queryset.filter(local_id=local_id)
        return queryset

    def get_by_codigo(
        self,
        codigo: str,
        exclude_id: int | None = None,
    ) -> Edificio | None:
        """Busca un código incluyendo edificios retirados."""
        queryset = self.model.objects.filter(codigo__iexact=codigo)
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.first()

    def get_estadisticas(self) -> dict:
        """Calcula indicadores generales de edificios y espacios asignados."""
        edificios = self.model.objects.filter(is_deleted=False)
        espacios = Espacio.objects.filter(
            is_deleted=False,
            edificio__is_deleted=False,
        )
        return {
            'total': edificios.count(),
            'activos': edificios.filter(activo=True).count(),
            'espacios': espacios.count(),
            'pisos': espacios.values('edificio_id', 'piso').distinct().count(),
            'laboratorios': espacios.filter(tipo='laboratorio').count(),
            'aulas': espacios.filter(tipo='aula').count(),
        }

    def get_excel_catalog_data(self, edificios, local_id: int | None = None):
        """Obtiene las métricas y filas necesarias para exportar pabellones."""
        from equipos.models import Equipo
        from espacios.models import Local

        local = Local.objects.filter(id=local_id).first() if local_id else None
        total_buildings = len(edificios)
        total_spaces = sum(building.cantidad_espacios for building in edificios)
        total_laboratories = sum(building.cantidad_laboratorios for building in edificios)
        total_equipment = Equipo.objects.filter(
            espacio__edificio__in=edificios,
            is_deleted=False,
        ).count()
        stats = {
            'total_pabellones': total_buildings,
            'total_ambientes': total_spaces,
            'total_laboratorios': total_laboratories,
            'total_equipos': total_equipment,
        }

        rows = []
        for building in edificios:
            equipment_count = Equipo.objects.filter(
                espacio__edificio=building,
                is_deleted=False,
            ).count()
            rows.append({
                "sede": building.local.nombre if building.local else "—",
                "codigo": building.codigo,
                "nombre": building.nombre,
                "pisos": building.cantidad_pisos,
                "espacios": building.cantidad_espacios,
                "laboratorios": building.cantidad_laboratorios,
                "aulas": building.cantidad_aulas,
                "equipos": equipment_count,
                "estado": "Activo" if building.activo else "Inactivo",
            })
        return local, stats, rows

    def get_excel_floor_data(self, building: Edificio, floor: str):
        """Obtiene métricas y filas de equipos y espacios de un piso."""
        from equipos.models import Equipo

        spaces = Espacio.objects.filter(
            edificio=building,
            piso=floor,
            is_deleted=False,
        ).prefetch_related('equipos', 'asignaciones_usuario__usuario')
        equipment = Equipo.objects.filter(espacio__in=spaces, is_deleted=False)
        total_spaces = spaces.count()
        total_equipment = equipment.count()
        operational_count = equipment.filter(estado='en_uso').count()
        maintenance_count = equipment.filter(estado='en_mantenimiento').count()
        damaged_count = equipment.filter(estado='dañado').count()
        stats = {
            'total_ambientes': total_spaces,
            'total_equipos': total_equipment,
            'equipos_operativos': operational_count,
            'equipos_mantenimiento': maintenance_count,
            'equipos_dañados': damaged_count,
        }

        rows = []
        for space in spaces:
            space_equipment = list(space.equipos.filter(is_deleted=False))
            assignments = [
                f"{assignment.usuario.nombre} {assignment.usuario.apellido}".strip()
                for assignment in space.asignaciones_usuario.filter(is_deleted=False, activo=True)
            ]
            rows.append({
                "codigo_espacio": space.codigo_espacio,
                "tipo": space.get_tipo_display(),
                "equipos_operativos": sum(1 for item in space_equipment if item.estado == 'en_uso'),
                "equipos_mantenimiento": sum(
                    1 for item in space_equipment if item.estado == 'en_mantenimiento'
                ),
                "equipos_dañados": sum(1 for item in space_equipment if item.estado == 'dañado'),
                "total_equipos": len(space_equipment),
                "responsables": ", ".join(assignments) if assignments else "Sin asignar",
                "estado": "Activo" if space.activo else "Inactivo",
            })
        return stats, rows

    def local_asignable(self, local_id: int):
        """Busca un local vigente y activo para asignarlo a un edificio."""
        from espacios.models import Local

        return Local.objects.filter(
            id=local_id,
            is_deleted=False,
            activo=True,
        ).first()

    def get_space_ids_for_floor(self, building_id: int, floor: str) -> set[int]:
        """Obtiene los ambientes activos que deben aparecer en el croquis del piso."""
        normalized_floor = floor.strip()
        floor_query = Q(piso__iexact=normalized_floor) | Q(
            piso__iexact=f'Piso {normalized_floor}'
        )
        return set(Espacio.objects.filter(
            floor_query,
            edificio_id=building_id,
            activo=True,
            is_deleted=False,
        ).values_list('id', flat=True))

    @transaction.atomic
    def update_with_spaces(self, instance: Edificio, **kwargs) -> Edificio:
        """Actualiza el edificio y sincroniza su nombre con el pabellón histórico."""
        nombre_anterior = instance.nombre
        updated = self.update(instance, **kwargs)
        if updated.nombre != nombre_anterior:
            updated.espacios.filter(is_deleted=False).update(pabellon=updated.nombre)
        return updated

    @transaction.atomic
    def soft_delete(self, instance: Edificio, actor: Usuario) -> None:
        """Retira el edificio y conserva sus espacios como registros independientes."""
        instance.espacios.filter(is_deleted=False).update(edificio=None)
        instance.activo = False
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(
            update_fields=['activo', 'is_deleted', 'updated_by', 'updated_at']
        )

    def restore(self, instance: Edificio, data: dict, actor: Usuario) -> Edificio:
        """Restaura un edificio retirado reutilizando su código único."""
        for field, value in data.items():
            setattr(instance, field, value)
        instance.activo = data.get('activo', True)
        instance.is_deleted = False
        instance.updated_by = actor
        instance.save()
        return self.get_by_id(instance.id)
