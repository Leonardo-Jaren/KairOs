from django.db.models import Prefetch, Q

from equipos.models import Equipo
from espacios.models import Espacio, EspacioUsuario
from shared.base_repository import BaseRepository
from usuarios.models import Usuario


class EspacioRepository(BaseRepository):
    """Centraliza las consultas y persistencia de espacios."""

    model = Espacio

    def get_all(self):
        """Retorna espacios vigentes con responsables y equipos precargados."""
        asignaciones = EspacioUsuario.objects.filter(
            is_deleted=False,
            activo=True,
        ).select_related('usuario').order_by('tipo_responsabilidad', 'usuario__nombre')
        equipos = Equipo.objects.filter(is_deleted=False).order_by('codigo')
        return self.model.objects.filter(is_deleted=False).prefetch_related(
            Prefetch(
                'asignaciones_usuario',
                queryset=asignaciones,
                to_attr='asignaciones_activas',
            ),
            Prefetch(
                'equipos',
                queryset=equipos,
                to_attr='equipos_vigentes',
            ),
        )

    def get_by_id(self, id: int) -> Espacio | None:
        """Busca un espacio vigente por identificador."""
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(
        self,
        busqueda: str = '',
        tipo: str = '',
        activo: bool | None = None,
        pabellon: str = '',
    ):
        """Aplica los filtros disponibles en la pantalla de espacios."""
        queryset = self.get_all()
        if busqueda:
            queryset = queryset.filter(
                Q(codigo_espacio__icontains=busqueda)
                | Q(pabellon__icontains=busqueda)
                | Q(piso__icontains=busqueda)
                | Q(asignaciones_usuario__usuario__nombre__icontains=busqueda)
                | Q(asignaciones_usuario__usuario__apellido__icontains=busqueda)
            ).distinct()
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if activo is not None:
            queryset = queryset.filter(activo=activo)
        if pabellon:
            queryset = queryset.filter(pabellon__icontains=pabellon)
        return queryset

    def get_by_codigo(
        self,
        codigo: str,
        exclude_id: int | None = None,
    ) -> Espacio | None:
        """Busca un espacio por código incluyendo registros retirados."""
        queryset = self.model.objects.filter(codigo_espacio__iexact=codigo)
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.first()

    def get_estadisticas(self) -> dict:
        """Calcula indicadores generales del módulo."""
        espacios = self.model.objects.filter(is_deleted=False)
        return {
            'total': espacios.count(),
            'activos': espacios.filter(activo=True).count(),
            'laboratorios': espacios.filter(tipo='laboratorio', activo=True).count(),
            'equipos': Equipo.objects.filter(
                is_deleted=False,
                espacio__is_deleted=False,
            ).count(),
        }

    def soft_delete(self, instance: Espacio, actor: Usuario) -> None:
        """Retira el espacio conservando sus relaciones históricas."""
        instance.activo = False
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(
            update_fields=['activo', 'is_deleted', 'updated_by', 'updated_at']
        )

    def restore(self, instance: Espacio, data: dict, actor: Usuario) -> Espacio:
        """Restaura un espacio eliminado usando sus datos actualizados."""
        for field, value in data.items():
            setattr(instance, field, value)
        instance.activo = data.get('activo', True)
        instance.is_deleted = False
        instance.updated_by = actor
        instance.save()
        return self.get_by_id(instance.id)
