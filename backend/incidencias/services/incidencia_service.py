from django.utils import timezone

from incidencias.repositories.incidencia_repository import IncidenciaRepository
from incidencias.models import Incidencia
from incidencias.exceptions import (
    IncidenciaNoEncontrada,
    TecnicoNoEncontrado,
    MantenimientoNoEncontrado,
    DatosInvalidos,
)


class IncidenciaService:
    """
    SRP  — sólo gestiona la lógica de negocio de incidencias.
    DIP  — depende de la abstracción IncidenciaRepository.
    OCP  — nuevas transiciones de estado se añaden sin modificar las existentes.
    """

    # Mapa de transiciones válidas de estado
    _TRANSICIONES = {
        Incidencia.Estado.PENDIENTE:   {Incidencia.Estado.EN_REVISION},
        Incidencia.Estado.EN_REVISION: {Incidencia.Estado.RESUELTA},
        Incidencia.Estado.RESUELTA:    {Incidencia.Estado.CERRADA},
        Incidencia.Estado.CERRADA:     set(),
    }

    def __init__(self, incidencia_repository: IncidenciaRepository):
        self.repo = incidencia_repository

    # ------------------------------------------------------------------ #
    # GET                                                            #
    # ------------------------------------------------------------------ #

    def listar_incidencias(
        self,
        usuario_id:  int = None,
        espacio_id:  int = None,
        estado:      str = None,
    ) -> list:
        if usuario_id is not None:
            return self.repo.get_by_usuario(usuario_id)
        if espacio_id is not None:
            return self.repo.get_by_espacio(espacio_id)
        if estado is not None:
            return self.repo.get_by_estado(estado)
        return self.repo.get_all()

    def get_incidencia(self, incidencia_id: int) -> Incidencia:
        incidencia = self.repo.get_by_id(incidencia_id)
        if incidencia is None:
            raise IncidenciaNoEncontrada(
                f"Incidencia {incidencia_id} no encontrada"
            )
        return incidencia

    # ------------------------------------------------------------------ #
    # POST                                                                #
    # ------------------------------------------------------------------ #

    def crear_incidencia(self, datos: dict, usuario) -> Incidencia:
        """Cualquier usuario autenticado puede reportar una incidencia."""
        datos['usuario'] = usuario
        return self.repo.create(**datos)

    # ------------------------------------------------------------------ #
    # Máquina de estados                                                   #
    # ------------------------------------------------------------------ #

    def _validar_transicion(self, incidencia: Incidencia, nuevo_estado: str) -> None:
        permitidos = self._TRANSICIONES.get(incidencia.estado, set())
        if nuevo_estado not in permitidos:
            raise DatosInvalidos(
                f"No se puede pasar de '{incidencia.estado}' a '{nuevo_estado}'. "
                f"Transiciones permitidas: {permitidos or 'ninguna'}"
            )

    def asignar_tecnico(self, incidencia_id: int, tecnico_id: int) -> Incidencia:
        """
        Pendiente → En revisión.
        Asigna el técnico y registra la fecha de asignación.
        """
        from usuarios.models import PerfilTecnico

        incidencia = self.get_incidencia(incidencia_id)
        self._validar_transicion(incidencia, Incidencia.Estado.EN_REVISION)

        tecnico = PerfilTecnico.objects.filter(id_tecnico=tecnico_id).first()
        if tecnico is None:
            raise TecnicoNoEncontrado(f"Técnico {tecnico_id} no encontrado")

        return self.repo.update(
            incidencia,
            estado=Incidencia.Estado.EN_REVISION,
            tecnico_asignado=tecnico,
            fecha_asignacion=timezone.now(),
        )

    def resolver_incidencia(self, incidencia_id: int, solucion: str) -> Incidencia:
        """
        En revisión → Resuelta.
        Registra la solución y la fecha de resolución.
        """
        incidencia = self.get_incidencia(incidencia_id)
        self._validar_transicion(incidencia, Incidencia.Estado.RESUELTA)

        if not solucion or not solucion.strip():
            raise DatosInvalidos("Debe indicar la solución aplicada")

        return self.repo.update(
            incidencia,
            estado=Incidencia.Estado.RESUELTA,
            solucion=solucion.strip(),
            fecha_resolucion=timezone.now(),
        )

    def cerrar_incidencia(self, incidencia_id: int) -> Incidencia:
        """
        Resuelta → Cerrada.
        Archiva definitivamente la incidencia.
        """
        incidencia = self.get_incidencia(incidencia_id)
        self._validar_transicion(incidencia, Incidencia.Estado.CERRADA)
        return self.repo.update(incidencia, estado=Incidencia.Estado.CERRADA)

    # ------------------------------------------------------------------ #
    # Vínculo con mantenimiento                                            #
    # ------------------------------------------------------------------ #

    def vincular_mantenimiento(
        self,
        incidencia_id:    int,
        mantenimiento_id: int,
    ) -> Incidencia:
        """Asocia un ticket de mantenimiento generado a raíz de esta incidencia."""
        from mantenimiento.models import Mantenimiento

        incidencia = self.get_incidencia(incidencia_id)
        if incidencia.estado == Incidencia.Estado.CERRADA:
            raise DatosInvalidos(
                "No se puede modificar una incidencia ya cerrada"
            )

        mantenimiento = Mantenimiento.objects.filter(
            id_mantenimiento=mantenimiento_id
        ).first()
        if mantenimiento is None:
            raise MantenimientoNoEncontrado(
                f"Mantenimiento {mantenimiento_id} no encontrado"
            )

        return self.repo.update(incidencia, mantenimiento=mantenimiento)
