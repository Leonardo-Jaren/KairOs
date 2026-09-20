from rest_framework.exceptions import ValidationError

from shared.base import BaseService
from shared.mixins import AuditableMixin
from usuarios.models import Usuario
from usuarios.repositories.usuario_repository import UsuarioRepository


class UsuarioService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio de administración de usuarios."""

    ALTA                  = 'usuario.alta'
    ACTUALIZACION         = 'usuario.actualizacion'
    DESACTIVACION         = 'usuario.desactivacion'
    CAMBIO_ROL            = 'usuario.cambio_rol'
    PERMISOS_ACTUALIZADOS = 'usuario.permisos_actualizados'

    def __init__(self):
        self.repository = UsuarioRepository()

    def listar(
        self,
        actor: Usuario,
        busqueda: str = '',
        rol: str = '',
        activo: bool | None = None,
        local_id: int | None = None,
        supervisor_id: int | None = None,
    ):
        sede_ids = None
        filter_local_id = local_id
        if actor.rol not in ('superadmin',) and not actor.is_superuser:
            user_sedes = list(actor.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
            if user_sedes:
                if local_id:
                    if local_id not in user_sedes:
                        raise ValidationError({'local_id': 'No tienes acceso a la sede seleccionada.'})
                    sede_ids = [local_id]
                else:
                    sede_ids = user_sedes
                filter_local_id = None


        return self.repository.listar(
            busqueda=busqueda.strip(),
            rol=rol,
            activo=activo,
            solo_docentes=False,
            local_id=filter_local_id,
            sede_ids=sede_ids,
            supervisor_id=supervisor_id,
        )


    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    def _do_create(self, data: dict, actor=None) -> Usuario:
        clean_data = data.copy()
        sede_ids = clean_data.pop('sede_ids', None)
        sede_principal_id = clean_data.pop('sede_principal_id', None)
        resulting_role = clean_data.get('rol', 'usuario')
        if actor and actor.rol == 'responsable' and 'supervisor_id' not in clean_data:
            clean_data['supervisor_id'] = actor.id
        if resulting_role == 'docente':
            clean_data['supervisor_id'] = None
        supervisor_id = clean_data.get('supervisor_id', None)

        self._validar_actor(
            actor,
            clean_data.get('rol', 'usuario'),
            supervisor_id=supervisor_id,
            sede_ids=sede_ids,
        )
        self._validar_supervisor(None, supervisor_id, resulting_role=resulting_role)
        self._validar_unicidad(clean_data)
        if not sede_ids:
            raise ValidationError({'sede_ids': 'Debes asignar una sede física al usuario.'})

        clean_data['correo'] = clean_data['correo'].strip().lower()
        clean_data['username'] = clean_data['username'].strip()
        usuario = self.repository.create(**clean_data)

        if sede_ids is not None:
            self.repository.asignar_sedes(
                usuario,
                sede_ids=sede_ids,
                sede_principal_id=sede_principal_id,
                actor=actor,
            )

        return usuario

    def _do_update(self, id: int, data: dict, actor=None) -> Usuario:
        instance = self.get_by_id(id)
        clean_data = data.copy()
        sede_ids = clean_data.pop('sede_ids', None)
        sede_principal_id = clean_data.pop('sede_principal_id', None)
        resulting_role = clean_data.get('rol', instance.rol)
        if resulting_role == 'docente':
            clean_data['supervisor_id'] = None
        supervisor_id = clean_data.get('supervisor_id', instance.supervisor_id)

        self._validar_actor(
            actor,
            clean_data.get('rol', instance.rol),
            instance=instance,
            supervisor_id=supervisor_id,
            sede_ids=sede_ids,
        )
        if 'supervisor_id' in clean_data:
            self._validar_supervisor(instance.id, clean_data['supervisor_id'], resulting_role=resulting_role)
        self._validar_unicidad(clean_data, exclude_id=instance.id)
        if sede_ids is not None and not sede_ids:
            raise ValidationError({'sede_ids': 'El usuario debe conservar al menos una sede física.'})

        if 'correo' in clean_data:
            clean_data['correo'] = clean_data['correo'].strip().lower()
        if 'username' in clean_data:
            clean_data['username'] = clean_data['username'].strip()

        updated_usuario = self.repository.update(instance, **clean_data)

        if sede_ids is not None:
            self.repository.asignar_sedes(
                updated_usuario,
                sede_ids=sede_ids,
                sede_principal_id=sede_principal_id,
                actor=actor,
            )

        return updated_usuario

    def _do_delete(self, id: int, actor=None) -> Usuario:
        instance = self.get_by_id(id)
        self._validar_actor(actor, instance.rol, instance=instance)
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

    def _audit_on_update(self, cambios: list, instance, actor, ctx: dict | None = None):
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

    # ── Métodos auxiliares y de negocio ────────────────────────────────────────

    def get_by_correo(self, correo: str) -> Usuario | None:
        return self.repository.get_by_correo(correo)

    def get_estadisticas(self, actor: Usuario) -> dict:
        sede_ids = None
        if actor.rol not in ('superadmin',) and not actor.is_superuser:
            user_sedes = list(actor.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
            if user_sedes:
                sede_ids = user_sedes
        return self.repository.get_estadisticas(
            solo_docentes=False,
            sede_ids=sede_ids,
        )

    def get_organigrama(self, actor: Usuario, local_id: int | None = None) -> dict:
        """Retorna el organigrama jerárquico estructurado y los metadatos de sede."""
        sede_ids = None
        if actor.rol not in ('superadmin',) and not actor.is_superuser:
            actor_sedes = list(actor.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
            if actor_sedes:
                if local_id and local_id not in actor_sedes:
                    raise ValidationError({'local_id': 'No tienes acceso a la sede seleccionada.'})
                if not local_id:
                    sede_ids = actor_sedes

        arbol = self.repository.get_organigrama(local_id=local_id, sede_ids=sede_ids)

        sede_info = None
        if local_id:
            from espacios.models import Local
            try:
                local_obj = Local.objects.get(id=local_id)
                sede_info = {
                    'id': local_obj.id,
                    'codigo': local_obj.codigo,
                    'nombre': local_obj.nombre,
                    'ciudad': local_obj.ciudad,
                }
            except Local.DoesNotExist:
                pass

        def _flatten(nodes):
            flat = []
            for n in nodes:
                flat.append(n)
                if n.get('children'):
                    flat.extend(_flatten(n['children']))
            return flat

        todos_los_nodos = _flatten(arbol)

        # Clasificación por grupos funcionales:
        # 1. arbol_mando: Árboles jerárquicos activos o autoridades principales
        arbol_mando = [n for n in arbol if len(n.get('children', [])) > 0 or n.get('rol') == 'superadmin']
        if not arbol_mando and arbol:
            arbol_mando = [n for n in arbol if n.get('rol') in ('superadmin', 'admin')]
        if not arbol_mando and arbol:
            arbol_mando = [n for n in arbol if n.get('rol') == 'responsable']

        mando_ids = {n['id'] for n in arbol_mando}

        # 2. docentes: Claustro docente independiente
        docentes = [n for n in arbol if n.get('rol') == 'docente']

        # 3. sin_supervisor: Personal activo no docente que no encabeza la línea de mando
        sin_supervisor = [n for n in arbol if n.get('rol') != 'docente' and n['id'] not in mando_ids]

        # 4. sin_sede: Nodos en la vista sin ninguna sede física asignada
        sin_sede = [n for n in todos_los_nodos if not n.get('sedes')]

        total_nodos = len(todos_los_nodos)

        meta = {
            'total': total_nodos,
            'total_mando': sum(1 + self._count_children(n) for n in arbol_mando),
            'total_sin_supervisor': len(sin_supervisor),
            'total_docentes': len(docentes),
            'total_sin_sede': len(sin_sede),
        }

        grupos = {
            'arbol_mando': arbol_mando,
            'sin_supervisor': sin_supervisor,
            'docentes': docentes,
            'sin_sede': sin_sede,
        }

        return {
            'sede': sede_info,
            'total_nodos': total_nodos,
            'arbol': arbol,
            'meta': meta,
            'grupos': grupos,
        }

    def _count_children(self, node: dict, visited: set | None = None) -> int:
        if visited is None:
            visited = set()
        node_id = node.get('id')
        if node_id in visited:
            return 0
        if node_id is not None:
            visited.add(node_id)
        return sum(1 + self._count_children(c, visited) for c in node.get('children', []))

    def get_permisos(self, usuario_id: int, actor: Usuario | None = None) -> dict:
        """Obtiene la configuración de permisos del usuario verificando alcance del actor."""
        usuario = self.get_by_id(usuario_id)
        if actor and actor.rol not in ('superadmin',) and not actor.is_superuser:
            if actor.id != usuario.id and actor.rol not in ('admin', 'responsable'):
                raise ValidationError({'detail': 'No tienes permisos para consultar los accesos de este usuario.'})
            actor_sedes = set(actor.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
            if actor_sedes:
                target_sedes = set(usuario.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
                if target_sedes and not target_sedes.intersection(actor_sedes):
                    raise ValidationError({'detail': 'No tienes acceso a usuarios de otra sede.'})

        from shared.constants import ROL_PERMISOS_BASE, MODULOS_SISTEMA, ACCIONES_SISTEMA

        permisos_custom = list(
            self.repository.get_permisos_personalizados(usuario_id).values('modulo', 'accion', 'permitido')
        )
        return {
            'usuario_id': usuario.id,
            'nombre_completo': f"{usuario.nombre} {usuario.apellido}".strip(),
            'rol': usuario.rol,
            'modulos': [m[0] for m in MODULOS_SISTEMA],
            'acciones': ACCIONES_SISTEMA,
            'permisos_base': ROL_PERMISOS_BASE.get(usuario.rol, {}),
            'permisos_personalizados': permisos_custom,
            'permisos_efectivos': usuario.get_permisos_efectivos(),
        }

    def guardar_permisos(self, usuario_id: int, permisos_data: list[dict], actor: Usuario) -> dict:
        """Guarda o actualiza permisos personalizados y registra auditoría."""
        target_usuario = self.get_by_id(usuario_id)
        if actor.rol not in ('superadmin', 'admin') and not actor.is_superuser:
            raise ValidationError({'detail': 'No tienes permisos para modificar la matriz de accesos.'})
        if actor.rol == 'admin':
            if target_usuario.rol in ('superadmin', 'admin') and target_usuario.id != actor.id:
                raise ValidationError({'detail': 'No puedes editar los permisos de otros administradores.'})
            actor_sedes = set(actor.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
            if actor_sedes:
                target_sedes = set(target_usuario.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
                if target_sedes and not target_sedes.intersection(actor_sedes):
                    raise ValidationError({'detail': 'No puedes editar permisos de usuarios de otra sede.'})

        self.repository.guardar_permisos_personalizados(usuario_id, permisos_data, actor=actor)
        self._audit_registrar(
            target_usuario,
            self.PERMISOS_ACTUALIZADOS,
            actor,
            f'Permisos personalizados actualizados para {target_usuario.username}.',
            datos_extra={'permisos': permisos_data},
        )
        return self.get_permisos(usuario_id, actor=actor)

    def reset_permisos(self, usuario_id: int, actor: Usuario) -> dict:
        """Restablece los permisos a los valores predeterminados del rol."""
        target_usuario = self.get_by_id(usuario_id)
        if actor.rol not in ('superadmin', 'admin') and not actor.is_superuser:
            raise ValidationError({'detail': 'No tienes permisos para restablecer permisos.'})
        if actor.rol == 'admin':
            if target_usuario.rol in ('superadmin', 'admin') and target_usuario.id != actor.id:
                raise ValidationError({'detail': 'No puedes restablecer los permisos de otros administradores.'})
            actor_sedes = set(actor.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
            if actor_sedes:
                target_sedes = set(target_usuario.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
                if target_sedes and not target_sedes.intersection(actor_sedes):
                    raise ValidationError({'detail': 'No puedes restablecer permisos de usuarios de otra sede.'})

        self.repository.reset_permisos_personalizados(usuario_id)
        self._audit_registrar(
            target_usuario,
            self.PERMISOS_ACTUALIZADOS,
            actor,
            f'Permisos de {target_usuario.username} restablecidos a los valores por defecto del rol {target_usuario.rol}.',
        )
        return self.get_permisos(usuario_id, actor=actor)

    def get_actividad(self, usuario_id: int, actor: Usuario | None = None, limit: int = 20) -> list[dict]:
        """Consulta los últimos eventos de auditoría generados por el usuario."""
        target_usuario = self.get_by_id(usuario_id)
        if actor and actor.rol not in ('superadmin',) and not actor.is_superuser:
            if actor.id != target_usuario.id:
                if actor.rol == 'responsable':
                    subordinados_ids = {s.id for s in self.repository.get_subordinados(actor.id, directos_solo=False)}
                    if target_usuario.id not in subordinados_ids:
                        raise ValidationError({'detail': 'Solo puedes consultar la actividad de usuarios a tu cargo.'})
                elif actor.rol == 'admin':
                    actor_sedes = set(actor.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
                    if actor_sedes:
                        target_sedes = set(target_usuario.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
                        if target_sedes and not target_sedes.intersection(actor_sedes):
                            raise ValidationError({'detail': 'No puedes consultar la actividad de usuarios de otra sede.'})
                else:
                    raise ValidationError({'detail': 'No tienes permisos para consultar la actividad de otros usuarios.'})

        from historial.models import Historial
        eventos = Historial.objects.filter(usuario_id=usuario_id).order_by('-fecha')[:limit]
        return [
            {
                'id': e.id,
                'fecha': e.fecha.isoformat(),
                'tipo_evento': e.tipo_evento,
                'descripcion': e.descripcion,
                'datos_extra': e.datos_extra,
            }
            for e in eventos
        ]


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

    def _validar_supervisor(
        self,
        instance_id: int | None,
        supervisor_id: int | None,
        resulting_role: str | None = None,
    ) -> None:
        if not supervisor_id:
            return
        if resulting_role == 'docente':
            raise ValidationError({'supervisor_id': 'Los docentes no tienen supervisor directo.'})
        if instance_id and supervisor_id == instance_id:
            raise ValidationError({'supervisor_id': 'Un usuario no puede ser su propio supervisor.'})

        try:
            supervisor = Usuario.objects.get(id=supervisor_id)
        except Usuario.DoesNotExist:
            raise ValidationError({'supervisor_id': 'El supervisor indicado no existe.'})

        if not supervisor.is_active:
            raise ValidationError({'supervisor_id': 'El supervisor indicado no está activo.'})
        if supervisor.rol not in ('superadmin', 'admin', 'responsable'):
            raise ValidationError({'supervisor_id': 'Solo un administrador o responsable puede ser supervisor.'})

        if instance_id:
            actual = supervisor
            while actual and actual.supervisor_id:
                if actual.supervisor_id == instance_id:
                    raise ValidationError({'supervisor_id': 'No se permite una relación jerárquica circular.'})
                actual = actual.supervisor

    def _validar_actor(
        self,
        actor: Usuario | None,
        resulting_role: str,
        instance: Usuario | None = None,
        supervisor_id: int | None = None,
        sede_ids: list[int] | None = None,
    ) -> None:
        if not actor:
            return

        if actor.rol == 'superadmin' or actor.is_superuser:
            return

        if actor.rol == 'tecnico':
            raise ValidationError({'detail': 'Los técnicos no tienen permisos para crear ni modificar usuarios.'})

        actor_sedes = set(actor.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))

        if actor.rol == 'admin':
            if instance and instance.id != actor.id and instance.rol in ('superadmin', 'admin'):
                raise ValidationError({'detail': 'Un administrador solo puede gestionar responsables y personal de menor jerarquía.'})
            if not instance and resulting_role == 'superadmin':
                raise ValidationError({'rol': 'Un administrador no puede asignar el rol de Superadministrador.'})
            if instance and instance.id == actor.id and resulting_role != actor.rol:
                raise ValidationError({'rol': 'No puedes cambiar tu propia jerarquía administrativa.'})
            if not instance and resulting_role not in ('admin', 'responsable', 'tecnico', 'docente', 'usuario'):
                raise ValidationError({'rol': 'El rol seleccionado no está dentro de tu alcance administrativo.'})

            if actor_sedes:
                if sede_ids is not None:
                    if not set(sede_ids).issubset(actor_sedes):
                        raise ValidationError({'sede_ids': 'Solo puedes asignar sedes bajo tu administración.'})
                if instance:
                    inst_sedes = set(instance.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
                    if instance.id != actor.id and inst_sedes and not inst_sedes.intersection(actor_sedes):
                        raise ValidationError({'detail': 'No puedes modificar usuarios de otra sede.'})
                if supervisor_id and supervisor_id != actor.id:
                    from usuarios.models import UsuarioSede
                    sup_sedes = set(UsuarioSede.objects.filter(usuario_id=supervisor_id, activo=True).values_list('local_id', flat=True))
                    if sup_sedes and not sup_sedes.intersection(actor_sedes):
                        raise ValidationError({'supervisor_id': 'El supervisor asignado debe pertenecer a tus sedes administradas.'})

        if actor.rol == 'responsable':
            is_self = bool(instance and instance.id == actor.id)
            if is_self:
                if resulting_role != actor.rol:
                    raise ValidationError({'rol': 'No puedes cambiar tu propia jerarquía.'})
            else:
                if resulting_role not in ('tecnico', 'docente', 'usuario'):
                    raise ValidationError({'rol': 'Los responsables solo pueden gestionar técnicos, docentes o usuarios a su cargo.'})
                if instance and instance.supervisor_id != actor.id:
                    raise ValidationError({'detail': 'Solo puedes gestionar usuarios que estén directamente a tu cargo.'})
                if not instance and supervisor_id not in (None, actor.id):
                    raise ValidationError({'supervisor_id': 'Un usuario creado por un responsable debe quedar a su cargo.'})

            if actor_sedes:
                if sede_ids is not None:
                    if not set(sede_ids).issubset(actor_sedes):
                        raise ValidationError({'sede_ids': 'Solo puedes asignar sedes bajo tu responsabilidad.'})
                if instance:
                    inst_sedes = set(instance.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))
                    if not is_self and inst_sedes and not inst_sedes.intersection(actor_sedes):
                        raise ValidationError({'detail': 'No puedes modificar usuarios de otra sede.'})
                if supervisor_id and supervisor_id != actor.id:
                    from usuarios.models import UsuarioSede
                    sup_sedes = set(UsuarioSede.objects.filter(usuario_id=supervisor_id, activo=True).values_list('local_id', flat=True))
                    if sup_sedes and not sup_sedes.intersection(actor_sedes):
                        raise ValidationError({'supervisor_id': 'El supervisor asignado debe pertenecer a tus sedes asignadas.'})

        if actor.rol in ('docente', 'usuario'):
            raise ValidationError({'detail': 'No tienes permisos para gestionar usuarios.'})
