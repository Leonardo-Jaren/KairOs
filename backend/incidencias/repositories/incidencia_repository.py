from django.db.models import Count, Q

from equipos.models import Equipo
from espacios.models import Espacio
from incidencias.models import Incidencia
from shared.base import BaseRepository


class IncidenciaRepository(BaseRepository):
    """Centraliza las consultas y persistencia de incidencias."""

    model = Incidencia

    def get_all(self):
        """Retorna incidencias vigentes con sus relaciones precargadas."""
        return self.model.objects.filter(is_deleted=False).select_related(
            'espacio', 'equipo', 'created_by'
        )

    def get_by_id(self, id: int) -> Incidencia | None:
        """Busca una incidencia vigente por identificador."""
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(
        self,
        busqueda: str = '',
        espacio_id: int | None = None,
        equipo_id: int | None = None,
        tipo_incidencia: str = '',
        estado: str = '',
        reportado_por_id: int | None = None,
    ):
        """Aplica los filtros disponibles en la pantalla de incidencias."""
        queryset = self.get_all()

        if busqueda:
            queryset = queryset.filter(
                Q(descripcion__icontains=busqueda)
                | Q(equipo__codigo__icontains=busqueda)
                | Q(espacio__codigo_espacio__icontains=busqueda)
            )
        if espacio_id is not None:
            queryset = queryset.filter(espacio_id=espacio_id)
        if equipo_id is not None:
            queryset = queryset.filter(equipo_id=equipo_id)
        if tipo_incidencia:
            queryset = queryset.filter(tipo_incidencia=tipo_incidencia)
        if estado:
            queryset = queryset.filter(estado=estado)
        if reportado_por_id is not None:
            queryset = queryset.filter(created_by_id=reportado_por_id)

        return queryset

    def get_estadisticas(self, reportado_por_id: int | None = None) -> dict:
        """Calcula indicadores generales del modulo de incidencias."""
        incidencias = self.model.objects.filter(is_deleted=False)
        if reportado_por_id is not None:
            incidencias = incidencias.filter(created_by_id=reportado_por_id)
        return incidencias.aggregate(
            total=Count('id'),
            pendientes=Count('id', filter=Q(estado='pendiente')),
            en_proceso=Count('id', filter=Q(estado='en_proceso')),
            resueltas=Count('id', filter=Q(estado='resuelto')),
        )

    def get_espacios_opciones(self):
        """Retorna espacios vigentes para poblar el select del formulario de incidencias."""
        return list(
            Espacio.objects.filter(is_deleted=False, activo=True)
            .order_by('codigo_espacio')
            .values('id', 'codigo_espacio', 'pabellon', 'tipo')
        )

    def get_equipos_opciones(self, espacio_id: int | None = None):
        """Retorna equipos vigentes para poblar el select del formulario de incidencias."""
        queryset = Equipo.objects.filter(is_deleted=False)
        if espacio_id is not None:
            queryset = queryset.filter(espacio_id=espacio_id)
        return list(
            queryset.order_by('codigo')
            .values('id', 'codigo', 'marca', 'modelo', 'tipo_equipo', 'espacio_id')
        )

    def soft_delete(self, instance: Incidencia, actor) -> None:
        """Elimina logicamente la incidencia."""
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(update_fields=['is_deleted', 'updated_by', 'updated_at'])
