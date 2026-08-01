from rest_framework.exceptions import ValidationError

from espacios.models import EspacioUsuario
from espacios.repositories import EspacioUsuarioRepository
from shared.base_service import BaseService
from usuarios.models import Usuario


class EspacioUsuarioService(BaseService):
    """Aplica reglas para asignar usuarios a espacios físicos."""

    def __init__(self):
        self.repository = EspacioUsuarioRepository()

    def listar(
        self,
        busqueda: str = '',
        activo: bool | None = None,
        usuario_id: int | None = None,
        espacio_id: int | None = None,
    ):
        """Lista asignaciones con filtros opcionales."""
        return self.repository.listar(
            busqueda=busqueda.strip(),
            activo=activo,
            usuario_id=usuario_id,
            espacio_id=espacio_id,
        )

    def create(self, data: dict, actor: Usuario) -> EspacioUsuario:
        """Crea una asignación válida y auditable."""
        clean_data = data.copy()
        usuario, espacio = self._resolver_relaciones(clean_data)
        existing = self.repository.get_by_pair(espacio.id, usuario.id)
        if existing and existing.is_deleted:
            return self.repository.restore(
                existing,
                clean_data.get('tipo_responsabilidad', 'responsable'),
                actor,
            )
        self._validar_unicidad(espacio.id, usuario.id)
        return self.repository.create(
            usuario=usuario,
            espacio=espacio,
            tipo_responsabilidad=clean_data.get(
                'tipo_responsabilidad',
                'responsable',
            ),
            activo=clean_data.get('activo', True),
            created_by=actor,
            updated_by=actor,
        )

    def update(
        self,
        id: int,
        data: dict,
        actor: Usuario,
    ) -> EspacioUsuario:
        """Actualiza una asignación validando sus relaciones y unicidad."""
        instance = self.get_by_id(id)
        clean_data = data.copy()
        usuario_id = clean_data.pop('usuario_id', instance.usuario_id)
        espacio_id = clean_data.pop('espacio_id', instance.espacio_id)
        usuario, espacio = self._resolver_relaciones({
            'usuario_id': usuario_id,
            'espacio_id': espacio_id,
        })
        self._validar_unicidad(espacio.id, usuario.id, exclude_id=instance.id)
        clean_data.update({
            'usuario': usuario,
            'espacio': espacio,
            'updated_by': actor,
        })
        return self.repository.update(instance, **clean_data)

    def delete(self, id: int, actor: Usuario) -> None:
        """Elimina lógicamente una asignación para conservar trazabilidad."""
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)

    def get_opciones(self) -> dict:
        """Entrega usuarios y espacios disponibles para el formulario."""
        return self.repository.get_opciones()

    def _resolver_relaciones(self, data: dict):
        """Resuelve identificadores y reporta relaciones inexistentes."""
        usuario = self.repository.get_usuario_by_id(data.get('usuario_id'))
        espacio = self.repository.get_espacio_by_id(data.get('espacio_id'))
        errors = {}
        if usuario is None:
            errors['usuario_id'] = 'El usuario no existe o está inactivo.'
        if espacio is None:
            errors['espacio_id'] = 'El espacio no existe o está eliminado.'
        if errors:
            raise ValidationError(errors)
        return usuario, espacio

    def _validar_unicidad(
        self,
        espacio_id: int,
        usuario_id: int,
        exclude_id: int | None = None,
    ) -> None:
        """Evita asignar dos veces la misma cuenta al mismo espacio."""
        existing = self.repository.get_by_pair(
            espacio_id,
            usuario_id,
            exclude_id,
        )
        if existing:
            raise ValidationError({
                'detail': 'El usuario ya está asignado a este espacio.'
            })
