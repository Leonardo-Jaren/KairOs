from rest_framework.exceptions import ValidationError

from shared.base_service import BaseService
from usuarios.models import Usuario
from usuarios.repositories.usuario_repository import UsuarioRepository


class UsuarioService(BaseService):
    """Aplica las reglas de negocio de administración de usuarios."""

    def __init__(self):
        self.repository = UsuarioRepository()

    def listar(
        self,
        actor: Usuario,
        busqueda: str = '',
        rol: str = '',
        activo: bool | None = None,
    ):
        """Lista cuentas respetando el alcance permitido para el actor."""
        return self.repository.listar(
            busqueda=busqueda.strip(),
            rol=rol,
            activo=activo,
            solo_docentes=actor.rol == 'tecnico',
        )

    def create(self, data: dict, actor: Usuario | None = None) -> Usuario:
        """Crea una cuenta después de validar unicidad y permisos de rol."""
        clean_data = data.copy()
        self._validar_actor(actor, clean_data.get('rol', 'usuario'))
        self._validar_unicidad(clean_data)
        clean_data['correo'] = clean_data['correo'].strip().lower()
        clean_data['username'] = clean_data['username'].strip()
        return self.repository.create(**clean_data)

    def update(
        self,
        id: int,
        data: dict,
        actor: Usuario | None = None,
    ) -> Usuario:
        """Actualiza una cuenta sin permitir duplicados ni escalamiento de rol."""
        instance = self.get_by_id(id)
        clean_data = data.copy()
        resulting_role = clean_data.get('rol', instance.rol)
        self._validar_actor(actor, resulting_role, instance)
        self._validar_unicidad(clean_data, exclude_id=instance.id)

        if 'correo' in clean_data:
            clean_data['correo'] = clean_data['correo'].strip().lower()
        if 'username' in clean_data:
            clean_data['username'] = clean_data['username'].strip()

        return self.repository.update(instance, **clean_data)

    def delete(self, id: int, actor: Usuario | None = None) -> None:
        """Desactiva una cuenta sin eliminar sus relaciones históricas."""
        instance = self.get_by_id(id)
        if actor and actor.id == instance.id:
            raise ValidationError({
                'detail': 'No puedes desactivar tu propia cuenta.'
            })
        self.repository.deactivate(instance)

    def get_by_correo(self, correo: str) -> Usuario | None:
        """Obtiene una cuenta mediante su correo electrónico."""
        return self.repository.get_by_correo(correo)

    def get_estadisticas(self, actor: Usuario) -> dict:
        """Retorna métricas agregadas del módulo de usuarios."""
        return self.repository.get_estadisticas(
            solo_docentes=actor.rol == 'tecnico'
        )

    def create_google_user(self, correo: str, nombre: str) -> Usuario:
        """Crea una cuenta externa con un nombre de usuario único."""
        base_username = correo.split('@')[0]
        username = base_username
        counter = 1

        while self.repository.username_exists(username):
            username = f'{base_username}{counter}'
            counter += 1

        return self.repository.create_user(
            correo=correo.strip().lower(),
            username=username,
            nombre=nombre,
            rol='usuario',
            is_active=True,
        )

    def _validar_unicidad(
        self,
        data: dict,
        exclude_id: int | None = None,
    ) -> None:
        """Valida campos únicos sin acceder al ORM fuera del repository."""
        correo = data.get('correo')
        username = data.get('username')
        errors = {}

        if correo and self.repository.correo_exists(correo, exclude_id):
            errors['correo'] = 'Ya existe un usuario con este correo electrónico.'
        if username and self.repository.username_exists(username, exclude_id):
            errors['username'] = 'Ya existe un usuario con este nombre de usuario.'

        if errors:
            raise ValidationError(errors)

    def _validar_actor(
        self,
        actor: Usuario | None,
        resulting_role: str,
        instance: Usuario | None = None,
    ) -> None:
        """Impide que un técnico gestione cuentas ajenas al rol docente."""
        if not actor or actor.rol != 'tecnico':
            return
        if resulting_role != 'docente' or (instance and instance.rol != 'docente'):
            raise ValidationError({
                'rol': 'Los técnicos solo pueden gestionar usuarios docentes.'
            })
