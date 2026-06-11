from django.utils import timezone

from mantenimiento.repositories.mantenimiento_repository import MantenimientoRepository
from mantenimiento.repositories.tecnico_mantenimiento_repository import TecnicoMantenimientoRepository
from mantenimiento.models import Mantenimiento, TecnicoMantenimiento
from mantenimiento.exceptions import MantenimientoNoEncontrado, TecnicoNoEncontrado, DatosInvalidos


class MantenimientoService:
    """
    SRP  — sólo gestiona la lógica de negocio de mantenimiento.
    DIP  — depende de abstracciones (repositorios), no de implementaciones.
    OCP  — las reglas de negocio se extienden sin modificar este servicio.
    """

    def __init__(
        self,
        mantenimiento_repository: MantenimientoRepository,
        tecnico_repository: TecnicoMantenimientoRepository,
    ):
        self.repo         = mantenimiento_repository
        self.tecnico_repo = tecnico_repository

    # ------------------------------------------------------------------ #
    # Consultas                                                            #
    # ------------------------------------------------------------------ #

    def listar_mantenimientos(
        self,
        equipo_id: int = None,
        solo_pendientes: bool = False,
    ) -> list:
        if equipo_id is not None:
            return self.repo.get_by_equipo(equipo_id)
        if solo_pendientes:
            return self.repo.get_pendientes()
        return self.repo.get_all()

    def get_mantenimiento(self, mantenimiento_id: int) -> Mantenimiento:
        mantenimiento = self.repo.get_by_id(mantenimiento_id)
        if mantenimiento is None:
            raise MantenimientoNoEncontrado(
                f"Mantenimiento {mantenimiento_id} no encontrado"
            )
        return mantenimiento

    # ------------------------------------------------------------------ #
    # Operaciones sobre mantenimientos                                     #
    # ------------------------------------------------------------------ #

    def crear_mantenimiento(self, datos: dict) -> Mantenimiento:
        """
        Al crear un ticket de mantenimiento el equipo pasa a estado
        'en mantenimiento' automáticamente.
        """
        equipo = datos["equipo"]
        equipo.estado = 'en mantenimiento'
        equipo.save(update_fields=["estado"])
        return self.repo.create(**datos)

    def actualizar_mantenimiento(self, mantenimiento_id: int, datos: dict) -> Mantenimiento:
        mantenimiento = self.get_mantenimiento(mantenimiento_id)
        if mantenimiento.estado == Mantenimiento.Estado.RESUELTO:
            raise DatosInvalidos("No se puede editar un mantenimiento ya cerrado")
        return self.repo.update(mantenimiento, **datos)

    def cerrar_mantenimiento(
        self,
        mantenimiento_id: int,
        datos: dict,
        usuario_cierre,
    ) -> Mantenimiento:
        """
        Cierra el ticket: registra fecha, observaciones y quién lo cerró.
        Restaura el equipo a estado 'no usado'.
        """
        mantenimiento = self.get_mantenimiento(mantenimiento_id)
        if mantenimiento.estado == Mantenimiento.Estado.RESUELTO:
            raise DatosInvalidos("Este mantenimiento ya fue cerrado")

        datos_cierre = {
            "estado":         Mantenimiento.Estado.RESUELTO,
            "fecha_cierre":   timezone.now().date(),
            "usuario_cierre": usuario_cierre,
            **datos,
        }
        mantenimiento = self.repo.update(mantenimiento, **datos_cierre)

        equipo = mantenimiento.equipo
        equipo.estado = 'no usado'
        equipo.save(update_fields=["estado"])

        return mantenimiento

    # ------------------------------------------------------------------ #
    # Asignación de técnicos                                               #
    # ------------------------------------------------------------------ #

    def asignar_tecnico(
        self,
        mantenimiento_id: int,
        tecnico_id: int,
    ) -> TecnicoMantenimiento:
        from usuarios.models import PerfilTecnico

        mantenimiento = self.get_mantenimiento(mantenimiento_id)
        if mantenimiento.estado == Mantenimiento.Estado.RESUELTO:
            raise DatosInvalidos(
                "No se pueden asignar técnicos a un mantenimiento cerrado"
            )
        if self.tecnico_repo.existe_asignacion(mantenimiento_id, tecnico_id):
            raise DatosInvalidos(
                "El técnico ya está asignado a este mantenimiento"
            )

        tecnico = PerfilTecnico.objects.filter(id_tecnico=tecnico_id).first()
        if tecnico is None:
            raise TecnicoNoEncontrado(f"Técnico {tecnico_id} no encontrado")

        return self.tecnico_repo.crear_asignacion(mantenimiento, tecnico)

    def remover_tecnico(self, mantenimiento_id: int, tecnico_id: int) -> None:
        self.get_mantenimiento(mantenimiento_id)
        eliminado = self.tecnico_repo.eliminar_asignacion(mantenimiento_id, tecnico_id)
        if not eliminado:
            raise DatosInvalidos(
                "El técnico no está asignado a este mantenimiento"
            )
