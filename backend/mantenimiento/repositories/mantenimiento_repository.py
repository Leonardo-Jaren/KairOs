from django.db.models import Count, Q

from equipos.models import Equipo
from mantenimiento.models import Mantenimiento, TecnicoMantenimiento
from shared.base import BaseRepository
from usuarios.models import PerfilTecnico, Usuario


class MantenimientoRepository(BaseRepository):
    """Centraliza las consultas y persistencia de tickets de mantenimiento."""

    model = Mantenimiento

    def get_all(self):
        """Retorna mantenimientos vigentes con equipo y tecnicos precargados."""
        return self.model.objects.filter(is_deleted=False).select_related(
            'equipo',
            'reportado_por',
        ).prefetch_related(
            'tecnicos_asignados__tecnico__usuario',
        )

    def get_by_id(self, id: int) -> Mantenimiento | None:
        """Busca un mantenimiento vigente por identificador."""
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(
        self,
        busqueda: str = '',
        estado: str = '',
        tipo_mantenimiento: str = '',
        equipo_id: int | None = None,
    ):
        """Aplica los filtros disponibles en la pantalla de mantenimiento."""
        queryset = self.get_all()

        if busqueda:
            queryset = queryset.filter(
                Q(equipo__codigo__icontains=busqueda)
                | Q(equipo__marca__icontains=busqueda)
                | Q(equipo__modelo__icontains=busqueda)
                | Q(descripcion__icontains=busqueda)
                | Q(tecnicos_asignados__tecnico__usuario__nombre__icontains=busqueda)
                | Q(tecnicos_asignados__tecnico__usuario__apellido__icontains=busqueda)
            ).distinct()
        if estado:
            queryset = queryset.filter(estado=estado)
        if tipo_mantenimiento:
            queryset = queryset.filter(tipo_mantenimiento=tipo_mantenimiento)
        if equipo_id is not None:
            queryset = queryset.filter(equipo_id=equipo_id)

        return queryset

    def get_equipo_by_id(self, equipo_id: int) -> Equipo | None:
        """Obtiene un equipo vigente disponible para asignar un ticket."""
        try:
            return Equipo.objects.get(id=equipo_id, is_deleted=False)
        except Equipo.DoesNotExist:
            return None

    def get_tecnicos_por_ids(self, tecnico_ids: list[int]):
        """Obtiene los perfiles tecnicos vigentes solicitados."""
        if not tecnico_ids:
            return PerfilTecnico.objects.none()
        return PerfilTecnico.objects.filter(
            id__in=tecnico_ids,
            is_deleted=False,
        ).select_related('usuario')

    def get_usuario_activo_by_id(self, usuario_id: int) -> Usuario | None:
        """Obtiene un usuario activo disponible como reportante."""
        try:
            return Usuario.objects.get(id=usuario_id, is_active=True)
        except Usuario.DoesNotExist:
            return None

    def sync_tecnicos(self, instance: Mantenimiento, tecnico_ids: list[int]) -> None:
        """Reemplaza las asignaciones de tecnicos de un ticket."""
        TecnicoMantenimiento.objects.filter(mantenimiento=instance).delete()
        if tecnico_ids:
            TecnicoMantenimiento.objects.bulk_create([
                TecnicoMantenimiento(mantenimiento=instance, tecnico_id=tecnico_id)
                for tecnico_id in tecnico_ids
            ])

    def get_estadisticas(self) -> dict:
        """Calcula indicadores generales para la cabecera del modulo."""
        tickets = self.model.objects.filter(is_deleted=False)
        return {
            **tickets.aggregate(
                total=Count('id'),
                pendientes=Count('id', filter=Q(estado='pendiente')),
                en_proceso=Count('id', filter=Q(estado='en_proceso')),
                resueltos=Count('id', filter=Q(estado='resuelto')),
                cancelados=Count('id', filter=Q(estado='cancelado')),
            ),
            'total_tecnicos': PerfilTecnico.objects.filter(is_deleted=False).count(),
            'total_dispositivos': Equipo.objects.filter(is_deleted=False).count(),
        }

    def get_tecnicos_disponibles(self):
        """Retorna tecnicos vigentes con datos minimos para formularios."""
        perfiles = PerfilTecnico.objects.filter(
            is_deleted=False,
            usuario__is_active=True,
        ).select_related('usuario').order_by('usuario__nombre', 'usuario__apellido')

        return [
            {
                'id': perfil.id,
                'usuario_id': perfil.usuario_id,
                'nombre_completo': f'{perfil.usuario.nombre} {perfil.usuario.apellido}'.strip(),
                'area': perfil.area,
            }
            for perfil in perfiles
        ]

    def soft_delete(self, instance: Mantenimiento, actor) -> None:
        """Retira el ticket de mantenimiento conservando su historial."""
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(update_fields=['is_deleted', 'updated_by', 'updated_at'])
