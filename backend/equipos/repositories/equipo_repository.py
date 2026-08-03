from django.db.models import Count, Q

from equipos.models import Equipo
from shared.base_repository import BaseRepository


class EquipoRepository(BaseRepository):
    """Centraliza las consultas y persistencia de equipos informaticos."""

    model = Equipo

    def get_all(self):
        """Retorna equipos vigentes con su espacio precargado."""
        return self.model.objects.filter(is_deleted=False).select_related('espacio')

    def get_by_id(self, id: int) -> Equipo | None:
        """Busca un equipo vigente por identificador."""
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(
        self,
        busqueda: str = '',
        tipo_equipo: str = '',
        estado: str = '',
        espacio_id: int | None = None,
    ):
        """Aplica los filtros disponibles en la pantalla de equipos."""
        queryset = self.get_all()

        if busqueda:
            queryset = queryset.filter(
                Q(codigo__icontains=busqueda)
                | Q(numero_serie__icontains=busqueda)
                | Q(marca__icontains=busqueda)
                | Q(modelo__icontains=busqueda)
            )
        if tipo_equipo:
            queryset = queryset.filter(tipo_equipo=tipo_equipo)
        if estado:
            queryset = queryset.filter(estado=estado)
        if espacio_id is not None:
            queryset = queryset.filter(espacio_id=espacio_id)

        return queryset

    def get_by_codigo(self, codigo: str, exclude_id: int | None = None) -> Equipo | None:
        """Busca un equipo por codigo incluyendo registros retirados."""
        queryset = self.model.objects.filter(codigo__iexact=codigo)
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.first()

    def get_by_numero_serie(self, numero_serie: str, exclude_id: int | None = None) -> Equipo | None:
        """Busca un equipo por numero de serie incluyendo registros retirados."""
        queryset = self.model.objects.filter(numero_serie__iexact=numero_serie)
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.first()

    def get_estadisticas(self) -> dict:
        """Calcula indicadores generales del modulo de equipos."""
        equipos = self.model.objects.filter(is_deleted=False)
        return equipos.aggregate(
            total=Count('id'),
            en_uso=Count('id', filter=Q(estado='en_uso')),
            en_mantenimiento=Count('id', filter=Q(estado='en_mantenimiento')),
            de_baja=Count('id', filter=Q(estado='de_baja')),
        )

    def get_opciones(self):
        """Retorna opciones minimas de equipos vigentes para formularios."""
        return list(
            self.get_all()
            .order_by('codigo')
            .values('id', 'codigo', 'marca', 'modelo', 'tipo_equipo', 'estado')
        )

    def soft_delete(self, instance: Equipo, actor) -> None:
        """Retira el equipo conservando su historial de mantenimientos."""
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(update_fields=['is_deleted', 'updated_by', 'updated_at'])
