from typing import Optional
from historial.models import Historial


class HistorialRepository:
    """
    Repositorio de sólo lectura.

    ISP — no hereda BaseRepository porque ese contrato incluye delete(),
    una operación que jamás debe ejecutarse sobre el historial de auditoría.
    Exponer ese método sería violar la intención del módulo.
    """

    def _base_qs(self):
        return Historial.objects.select_related('usuario').order_by('-fecha')

    def get_all(self):
        return self._base_qs()

    def get_by_id(self, historial_id: int) -> Optional[Historial]:
        return self._base_qs().filter(id_historial=historial_id).first()

    def get_by_tabla(self, tabla: str):
        return self._base_qs().filter(tabla_afectada=tabla)

    def get_by_registro(self, tabla: str, registro_id: int):
        """Historial completo de un registro específico en una tabla."""
        return self._base_qs().filter(
            tabla_afectada=tabla,
            registro_id=registro_id,
        )

    def get_by_usuario(self, usuario_id: int):
        return self._base_qs().filter(usuario__id_usuario=usuario_id)

    def get_by_accion(self, accion: str):
        return self._base_qs().filter(accion=accion)

    def filtrar(
        self,
        tabla:       str = None,
        registro_id: int = None,
        usuario_id:  int = None,
        accion:      str = None,
        fecha_desde       = None,
        fecha_hasta       = None,
    ):
        """Filtrado combinado con todos los parámetros opcionales."""
        qs = self._base_qs()
        if tabla:
            qs = qs.filter(tabla_afectada=tabla)
        if registro_id is not None:
            qs = qs.filter(registro_id=registro_id)
        if usuario_id is not None:
            qs = qs.filter(usuario__id_usuario=usuario_id)
        if accion:
            qs = qs.filter(accion=accion)
        if fecha_desde:
            qs = qs.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__date__lte=fecha_hasta)
        return qs
