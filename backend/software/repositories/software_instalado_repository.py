from equipos.models import Equipo
from shared.base import BaseRepository
from software.models import ProductoSoftware, SoftwareInstalado


class SoftwareInstaladoRepository(BaseRepository):
    """Centraliza la persistencia del software asignado a los equipos."""

    model = SoftwareInstalado

    def get_all(self):
        """Retorna instalaciones vigentes con sus relaciones precargadas."""
        return (
            self.model.objects
            .filter(
                is_deleted=False,
                equipo__is_deleted=False,
                producto_software__is_deleted=False,
            )
            .select_related('equipo', 'producto_software')
            .order_by('producto_software__software', 'producto_software__version')
        )

    def get_by_id(self, id: int) -> SoftwareInstalado | None:
        """Busca una instalacion vigente por identificador."""
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(self, equipo_id: int | None = None):
        """Lista instalaciones y permite limitar el resultado a un equipo."""
        queryset = self.get_all()
        if equipo_id is not None:
            queryset = queryset.filter(equipo_id=equipo_id)
        return queryset

    def get_equipo_by_id(self, equipo_id: int) -> Equipo | None:
        """Busca un equipo que aun se encuentre vigente."""
        try:
            return Equipo.objects.get(id=equipo_id, is_deleted=False)
        except Equipo.DoesNotExist:
            return None

    def get_producto_by_id_for_update(
        self,
        producto_id: int,
    ) -> ProductoSoftware | None:
        """Bloquea el producto durante la asignacion para evitar sobreuso."""
        try:
            return ProductoSoftware.objects.select_for_update().get(
                id=producto_id,
                is_deleted=False,
            )
        except ProductoSoftware.DoesNotExist:
            return None

    def get_by_equipo_producto_including_deleted(
        self,
        equipo_id: int,
        producto_id: int,
    ) -> SoftwareInstalado | None:
        """Busca la relacion incluso si fue retirada previamente."""
        return self.model.objects.filter(
            equipo_id=equipo_id,
            producto_software_id=producto_id,
        ).first()

    def count_active_by_producto(self, producto_id: int) -> int:
        """Cuenta las licencias que actualmente estan asignadas."""
        return self.model.objects.filter(
            producto_software_id=producto_id,
            is_deleted=False,
            equipo__is_deleted=False,
        ).count()

    def restore(
        self,
        instance: SoftwareInstalado,
        *,
        numero_licencia_usado: str,
        fecha_instalacion,
        actor,
    ) -> SoftwareInstalado:
        """Reactiva una asignacion retirada conservando su identidad."""
        instance.numero_licencia_usado = numero_licencia_usado
        instance.fecha_instalacion = fecha_instalacion
        instance.is_deleted = False
        instance.updated_by = actor
        instance.save(
            update_fields=[
                'numero_licencia_usado',
                'fecha_instalacion',
                'is_deleted',
                'updated_by',
                'updated_at',
            ],
        )
        return instance

    def soft_delete(self, instance: SoftwareInstalado, actor) -> None:
        """Retira logicamente una instalacion para preservar su historial."""
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(update_fields=['is_deleted', 'updated_by', 'updated_at'])
