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
        return self.model.objects.filter(is_deleted=False).annotate(
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

    def listar(self, busqueda: str = '', activo: bool | None = None):
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
