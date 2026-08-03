from rest_framework.exceptions import ValidationError

from shared.base import BaseService
from shared.mixins import AuditableMixin
from usuarios.models import Usuario
from usuarios.repositories.usuario_repository import UsuarioRepository


class UsuarioService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio de administración de usuarios."""

    ALTA          = 'usuario.alta'
    ACTUALIZACION = 'usuario.actualizacion'
    DESACTIVACION = 'usuario.desactivacion'
    CAMBIO_ROL    = 'usuario.cambio_rol'

    def __init__(self):
        self.repository = UsuarioRepository()

    def listar(
        self,
        actor: Usuario,
        busqueda: str = '',
        rol: str = '',
        activo: bool | None = None,
    ):
        return self.repository.listar(
            busqueda=busqueda.strip(),
            rol=rol,
            activo=activo,
            solo_docentes=actor.rol == 'tecnico',
        )

    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    def _do_create(self, data: dict, actor=None) -> Usuario:
        clean_data = data.copy()
        self._validar_actor(actor, clean_data.get('rol', 'usuario'))
        self._validar_unicidad(clean_data)
        clean_data['correo'] = clean_data['correo'].strip().lower()
        clean_data['username'] = clean_data['username'].strip()
        return self.repository.create(**clean_data)

    def _do_update(self, id: int, data: dict, actor=None) -> Usuario:
        instance = self.get_by_id(id)
        clean_data = data.copy()
        self._validar_actor(actor, clean_data.get('rol', instance.rol), instance)
        self._validar_unicidad(clean_data, exclude_id=instance.id)
        if 'correo' in clean_data:
            clean_data['correo'] = clean_data['correo'].strip().lower()
        if 'username' in clean_data:
            clean_data['username'] = clean_data['username'].strip()
        return self.repository.update(instance, **clean_data)

    def _do_delete(self, id: int, actor=None) -> Usuario:
        instance = self.get_by_id(id)
        if actor and actor.id == instance.id:
            raise ValidationError({'detail': 'No puedes desactivar tu propia cuenta.'})
        self.repository.deactivate(instance)
        return instance

    # ── Hooks de auditoría ─────────────────────────────────────────────────────

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        self._audit_registrar(
            instance, self.ALTA, actor,
            f'Cuenta {instance.username} registrada con rol {instance.rol}.',
        )

    def _audit_on_update(self, cambios: list, instance, actor):
        rol_cambio = next((c for c in cambios if c['campo'] == 'Rol'), None)
        if rol_cambio:
            self._audit_registrar(
                instance, self.CAMBIO_ROL, actor,
                f'Rol de {instance.username} cambiado de {rol_cambio["antes"]} a {rol_cambio["despues"]}.',
                datos_extra={'cambios': [rol_cambio]},
            )
        otros = [c for c in cambios if c['campo'] != 'Rol']
        if otros:
            self._audit_registrar(
                instance, self.ACTUALIZACION, actor,
                f'Datos de {instance.username} actualizados.',
                datos_extra={'cambios': otros},
            )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(
            instance, self.DESACTIVACION, actor,
            f'Cuenta {instance.username} desactivada.',
        )

    # ── Métodos auxiliares ─────────────────────────────────────────────────────

    def get_by_correo(self, correo: str) -> Usuario | None:
        return self.repository.get_by_correo(correo)

    def get_estadisticas(self, actor: Usuario) -> dict:
        return self.repository.get_estadisticas(solo_docentes=actor.rol == 'tecnico')

    def create_google_user(self, correo: str, nombre: str) -> Usuario:
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

    def _validar_unicidad(self, data: dict, exclude_id: int | None = None) -> None:
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
        if not actor or actor.rol != 'tecnico':
            return
        if resulting_role != 'docente' or (instance and instance.rol != 'docente'):
            raise ValidationError({'rol': 'Los técnicos solo pueden gestionar usuarios docentes.'})
