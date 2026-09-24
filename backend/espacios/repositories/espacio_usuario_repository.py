from django.db.models import Q

from espacios.models import Edificio, Espacio, EspacioUsuario, Local
from shared.base import BaseRepository
from usuarios.models import Usuario


class EspacioUsuarioRepository(BaseRepository):
    """Centraliza el acceso a datos de asignaciones territoriales usuario–espacio."""

    model = EspacioUsuario

    def get_all(self):
        """Retorna asignaciones vigentes con sus relaciones precargadas."""
        return self.model.objects.filter(is_deleted=False).select_related(
            'usuario',
            'local',
            'edificio',
            'edificio__local',
            'espacio',
            'espacio__edificio',
            'espacio__edificio__local',
        )

    def get_by_id(self, id: int) -> EspacioUsuario | None:
        """Busca una asignación vigente por identificador."""
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(
        self,
        busqueda: str = '',
        activo: bool | None = None,
        usuario_id: int | None = None,
        espacio_id: int | None = None,
        ambito: str | None = None,
        local_id: int | None = None,
        edificio_id: int | None = None,
        piso: str | None = None,
        sede_ids: list[int] | None = None,
        ordering: str | None = None,
    ):
        """Filtra asignaciones para la pantalla de gestión centralizada y consultas contextuales."""
        queryset = self.get_all()

        if activo is not None:
            queryset = queryset.filter(activo=activo)
        if usuario_id is not None:
            queryset = queryset.filter(usuario_id=usuario_id)
        if espacio_id is not None:
            queryset = queryset.filter(espacio_id=espacio_id)
        if ambito:
            queryset = queryset.filter(ambito=ambito)
        if local_id is not None:
            queryset = queryset.filter(local_id=local_id)
        if edificio_id is not None:
            queryset = queryset.filter(edificio_id=edificio_id)
        if piso:
            queryset = queryset.filter(piso=piso)
        if sede_ids is not None:
            queryset = queryset.filter(local_id__in=sede_ids)

        if busqueda:
            queryset = queryset.filter(
                Q(usuario__nombre__icontains=busqueda)
                | Q(usuario__apellido__icontains=busqueda)
                | Q(usuario__correo__icontains=busqueda)
                | Q(espacio__codigo_espacio__icontains=busqueda)
                | Q(espacio__pabellon__icontains=busqueda)
                | Q(edificio__nombre__icontains=busqueda)
                | Q(edificio__codigo__icontains=busqueda)
                | Q(local__nombre__icontains=busqueda)
                | Q(local__codigo__icontains=busqueda)
                | Q(piso__icontains=busqueda)
            )

        if ordering:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at', 'id')

        return queryset

    def get_by_scope(
        self,
        ambito: str,
        usuario_id: int,
        local_id: int | None = None,
        edificio_id: int | None = None,
        piso: str | None = None,
        espacio_id: int | None = None,
        exclude_id: int | None = None,
        only_active: bool = False,
    ) -> EspacioUsuario | None:
        """Busca una asignación según el nivel de ámbito y el usuario."""
        queryset = self.model.objects.filter(ambito=ambito, usuario_id=usuario_id)

        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        if only_active:
            queryset = queryset.filter(activo=True, is_deleted=False)

        if ambito == EspacioUsuario.AMBITO_SEDE:
            queryset = queryset.filter(local_id=local_id)
        elif ambito == EspacioUsuario.AMBITO_EDIFICIO:
            queryset = queryset.filter(edificio_id=edificio_id)
        elif ambito == EspacioUsuario.AMBITO_PISO:
            queryset = queryset.filter(edificio_id=edificio_id, piso=piso or '')
        elif ambito == EspacioUsuario.AMBITO_ESPACIO:
            queryset = queryset.filter(espacio_id=espacio_id)
        else:
            return None

        return queryset.first()

    def get_by_pair(
        self,
        espacio_id: int,
        usuario_id: int,
        exclude_id: int | None = None,
    ) -> EspacioUsuario | None:
        """Busca una relación por la combinación de espacio y usuario (compatibilidad legacy)."""
        queryset = self.model.objects.filter(
            espacio_id=espacio_id,
            usuario_id=usuario_id,
        )
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.first()

    def get_usuario_by_id(self, usuario_id: int) -> Usuario | None:
        """Obtiene una cuenta activa disponible para asignación."""
        try:
            return Usuario.objects.get(id=usuario_id, is_active=True)
        except Usuario.DoesNotExist:
            return None

    def get_local_by_id(self, local_id: int) -> Local | None:
        """Obtiene un local vigente disponible para asignación."""
        try:
            return Local.objects.get(id=local_id, is_deleted=False)
        except Local.DoesNotExist:
            return None

    def get_edificio_by_id(self, edificio_id: int) -> Edificio | None:
        """Obtiene un edificio vigente disponible para asignación."""
        try:
            return Edificio.objects.select_related('local').get(id=edificio_id, is_deleted=False)
        except Edificio.DoesNotExist:
            return None

    def get_espacio_by_id(self, espacio_id: int) -> Espacio | None:
        """Obtiene un espacio vigente disponible para asignación."""
        try:
            return Espacio.objects.select_related('edificio', 'edificio__local').get(
                id=espacio_id, is_deleted=False
            )
        except Espacio.DoesNotExist:
            return None

    def get_opciones(self, actor: Usuario = None) -> dict:
        """Retorna opciones mínimas para formularios de asignación a 4 niveles."""
        usuarios_qs = Usuario.objects.filter(is_active=True)
        locales_qs = Local.objects.filter(is_deleted=False, activo=True)
        edificios_qs = Edificio.objects.filter(is_deleted=False, activo=True)
        espacios_qs = Espacio.objects.filter(is_deleted=False, activo=True)

        # Si el actor es responsable, acotar catálogos a sus sedes autorizadas
        if actor and actor.rol == 'responsable' and not actor.is_superuser:
            actor_sedes = list(
                actor.usuario_sedes.filter(activo=True).values_list('local_id', flat=True)
            )
            if actor_sedes:
                locales_qs = locales_qs.filter(id__in=actor_sedes)
                edificios_qs = edificios_qs.filter(local_id__in=actor_sedes)
                espacios_qs = espacios_qs.filter(
                    Q(edificio__local_id__in=actor_sedes) | Q(edificio__isnull=True)
                )

        usuarios = list(
            usuarios_qs.order_by('nombre', 'apellido').values(
                'id', 'nombre', 'apellido', 'correo', 'rol'
            )
        )
        espacios = list(
            espacios_qs.order_by('codigo_espacio').values(
                'id', 'codigo_espacio', 'tipo', 'pabellon', 'piso', 'edificio_id'
            )
        )
        locales = list(
            locales_qs.order_by('nombre').values(
                'id', 'codigo', 'nombre', 'ciudad'
            )
        )
        edificios = list(
            edificios_qs.order_by('nombre').values(
                'id', 'codigo', 'nombre', 'local_id'
            )
        )
        return {
            'usuarios': usuarios,
            'espacios': espacios,
            'locales': locales,
            'edificios': edificios,
        }

    def soft_delete(self, instance: EspacioUsuario, actor: Usuario) -> None:
        """Marca una asignación como eliminada conservando auditoría."""
        instance.activo = False
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(
            update_fields=['activo', 'is_deleted', 'updated_by', 'updated_at']
        )

    def restore(
        self,
        instance: EspacioUsuario,
        tipo_responsabilidad: str,
        actor: Usuario,
        ambito: str | None = None,
        local: Local | None = None,
        edificio: Edificio | None = None,
        piso: str | None = None,
        espacio: Espacio | None = None,
    ) -> EspacioUsuario:
        """Reactiva una asignación retirada conservando su identidad."""
        instance.tipo_responsabilidad = tipo_responsabilidad
        instance.activo = True
        instance.is_deleted = False
        instance.updated_by = actor

        campos_actualizar = [
            'tipo_responsabilidad',
            'activo',
            'is_deleted',
            'updated_by',
            'updated_at',
        ]
        if ambito is not None:
            instance.ambito = ambito
            campos_actualizar.append('ambito')
        if local is not None:
            instance.local = local
            campos_actualizar.append('local')
        if edificio is not None:
            instance.edificio = edificio
            campos_actualizar.append('edificio')
        if piso is not None:
            instance.piso = piso
            campos_actualizar.append('piso')
        if espacio is not None:
            instance.espacio = espacio
            campos_actualizar.append('espacio')

        instance.save(update_fields=campos_actualizar)
        return instance
