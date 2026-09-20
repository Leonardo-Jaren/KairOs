from django.db.models import Count, Q

from shared.base import BaseRepository
from usuarios.models import PerfilTecnico, PermisoPersonalizado, Usuario, UsuarioSede


class UsuarioRepository(BaseRepository):
    """Centraliza todas las consultas y escrituras de usuarios."""

    model = Usuario

    def get_by_correo(self, correo: str) -> Usuario | None:
        """Busca un usuario por su correo electrónico normalizado."""
        try:
            return self.model.objects.get(correo__iexact=correo.strip())
        except self.model.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> Usuario | None:
        """Busca un usuario por su nombre de usuario."""
        try:
            return self.model.objects.get(username__iexact=username.strip())
        except self.model.DoesNotExist:
            return None

    def listar(
        self,
        busqueda: str = '',
        rol: str = '',
        activo: bool | None = None,
        solo_docentes: bool = False,
        local_id: int | None = None,
        sede_ids: list[int] | None = None,
        supervisor_id: int | None = None,
    ):
        """Retorna usuarios filtrados para la pantalla de administración."""
        queryset = self.model.objects.all().order_by('-id')

        if solo_docentes:
            queryset = queryset.filter(rol='docente')
        elif rol:
            queryset = queryset.filter(rol=rol)

        if activo is not None:
            queryset = queryset.filter(is_active=activo)

        if local_id:
            queryset = queryset.filter(usuario_sedes__local_id=local_id, usuario_sedes__activo=True).distinct()
        elif sede_ids:
            queryset = queryset.filter(usuario_sedes__local_id__in=sede_ids, usuario_sedes__activo=True).distinct()

        if supervisor_id:
            queryset = queryset.filter(supervisor_id=supervisor_id)

        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda)
                | Q(apellido__icontains=busqueda)
                | Q(correo__icontains=busqueda)
                | Q(username__icontains=busqueda)
                | Q(dni__icontains=busqueda)
            )

        return queryset

    def get_subordinados(self, usuario_id: int, directos_solo: bool = True) -> list[Usuario]:
        """Retorna la lista de usuarios subordinados directa o recursivamente."""
        if directos_solo:
            return list(self.model.objects.filter(supervisor_id=usuario_id, is_active=True).exclude(rol='docente'))

        subordinados = []
        pendientes = [usuario_id]
        visitados = {usuario_id}
        while pendientes:
            actual_id = pendientes.pop(0)
            hijos = list(self.model.objects.filter(supervisor_id=actual_id, is_active=True).exclude(rol='docente'))
            for hijo in hijos:
                if hijo.id not in visitados:
                    visitados.add(hijo.id)
                    subordinados.append(hijo)
                    pendientes.append(hijo.id)
        return subordinados

    def get_organigrama(
        self,
        local_id: int | None = None,
        sede_ids: list[int] | None = None,
    ) -> list[dict]:
        """
        Construye la estructura de árbol jerárquico de usuarios.
        Filtra por una sede concreta o por el conjunto de sedes permitido.
        """
        queryset = (
            self.model.objects.filter(is_active=True)
            .select_related('supervisor')
            .prefetch_related('usuario_sedes__local')
            .order_by('nombre')
        )
        if local_id:
            queryset = queryset.filter(usuario_sedes__local_id=local_id, usuario_sedes__activo=True).distinct()
        elif sede_ids:
            queryset = queryset.filter(
                usuario_sedes__local_id__in=sede_ids,
                usuario_sedes__activo=True,
            ).distinct()

        usuarios = list(queryset)

        nodes_by_id = {}
        for u in usuarios:
            sedes_data = [
                {
                    'id': us.local.id,
                    'codigo': us.local.codigo,
                    'nombre': us.local.nombre,
                    'es_sede_principal': us.es_sede_principal,
                }
                for us in u.usuario_sedes.all()
                if us.activo and hasattr(us, 'local') and us.local
            ]
            nodes_by_id[u.id] = {
                'id': u.id,
                'nombre': u.nombre,
                'apellido': u.apellido,
                'nombre_completo': f"{u.nombre} {u.apellido}".strip(),
                'username': u.username,
                'correo': u.correo,
                'dni': u.dni,
                'rol': u.rol,
                'is_active': u.is_active,
                # Los docentes no forman parte de la cadena de supervisión.
                'supervisor_id': None if u.rol == 'docente' else u.supervisor_id,
                'supervisor_nombre': (
                    f"{u.supervisor.nombre} {u.supervisor.apellido}".strip()
                    if u.rol != 'docente' and u.supervisor else None
                ),
                'sedes': sedes_data,
                'subordinados_count': 0,
                'children': [],
            }

        roots = []
        for u in usuarios:
            node = nodes_by_id[u.id]
            if u.rol != 'docente' and u.supervisor_id and u.supervisor_id in nodes_by_id and u.supervisor_id != u.id:
                parent_node = nodes_by_id[u.supervisor_id]
                parent_node['children'].append(node)
                parent_node['subordinados_count'] += 1
            else:
                roots.append(node)

        # Ordenar raíces colocando primero las que tienen descendientes jerárquicos
        roots.sort(
            key=lambda n: (
                0 if len(n.get('children', [])) > 0 else 1,
                0 if n.get('rol') in ('superadmin', 'admin') else 1,
                (n.get('nombre') or '').lower(),
            )
        )

        return roots

    def get_permisos_personalizados(self, usuario_id: int):
        """Retorna los permisos personalizados configurados para el usuario."""
        return PermisoPersonalizado.objects.filter(usuario_id=usuario_id)

    def guardar_permisos_personalizados(self, usuario_id: int, permisos_list: list[dict], actor=None):
        """Crea o actualiza permisos personalizados para el usuario."""
        for item in permisos_list:
            modulo = item.get('modulo')
            accion = item.get('accion')
            permitido = bool(item.get('permitido'))
            if modulo and accion:
                PermisoPersonalizado.objects.update_or_create(
                    usuario_id=usuario_id,
                    modulo=modulo,
                    accion=accion,
                    defaults={'permitido': permitido, 'updated_by': actor},
                )

    def reset_permisos_personalizados(self, usuario_id: int):
        """Elimina todas las personalizaciones para retornar a la plantilla base del rol."""
        PermisoPersonalizado.objects.filter(usuario_id=usuario_id).delete()

    def asignar_sedes(self, usuario: Usuario, sede_ids: list[int], sede_principal_id: int | None = None, actor=None):
        """Asigna sedes físicas (Locales) a un usuario."""
        UsuarioSede.objects.filter(usuario=usuario).exclude(local_id__in=sede_ids).update(activo=False)
        for idx, sid in enumerate(sede_ids):
            es_principal = (sid == sede_principal_id) if sede_principal_id else (idx == 0)
            UsuarioSede.objects.update_or_create(
                usuario=usuario,
                local_id=sid,
                defaults={
                    'activo': True,
                    'es_sede_principal': es_principal,
                    'updated_by': actor,
                },
            )

    def correo_exists(self, correo: str, exclude_id: int | None = None) -> bool:
        """Indica si el correo ya pertenece a otro usuario."""
        queryset = self.model.objects.filter(correo__iexact=correo.strip())
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()

    def username_exists(self, username: str, exclude_id: int | None = None) -> bool:
        """Indica si el nombre de usuario ya pertenece a otra cuenta."""
        queryset = self.model.objects.filter(username__iexact=username.strip())
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()

    def create_user(self, **kwargs) -> Usuario:
        """Crea una cuenta asegurando el tratamiento correcto de la contraseña."""
        password = kwargs.pop('password', None)
        user = self.model(**kwargs)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create(self, **kwargs) -> Usuario:
        """Delega la creación genérica al flujo seguro de usuarios."""
        return self.create_user(**kwargs)

    def update(self, instance: Usuario, **kwargs) -> Usuario:
        """Actualiza una cuenta y cifra una nueva contraseña cuando se recibe."""
        password = kwargs.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, **kwargs)

    def deactivate(self, instance: Usuario) -> Usuario:
        """Desactiva una cuenta conservando su historial y relaciones."""
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])
        return instance

    def get_estadisticas(self, solo_docentes: bool = False, sede_ids: list[int] | None = None) -> dict:
        """Calcula métricas resumidas para la pantalla de usuarios."""
        queryset = self.model.objects.all()
        if solo_docentes:
            queryset = queryset.filter(rol='docente')
        if sede_ids:
            queryset = queryset.filter(usuario_sedes__local_id__in=sede_ids, usuario_sedes__activo=True).distinct()
        return queryset.aggregate(
            total=Count('id'),
            activos=Count('id', filter=Q(is_active=True)),
            administradores=Count('id', filter=Q(rol='admin')),
            tecnicos=Count('id', filter=Q(rol='tecnico')),
            docentes=Count('id', filter=Q(rol='docente')),
        )


class PerfilTecnicoRepository(BaseRepository):
    """Gestiona el acceso a datos de los perfiles técnicos."""

    model = PerfilTecnico

    def get_by_usuario_id(self, usuario_id: int) -> PerfilTecnico | None:
        """Obtiene el perfil técnico asociado a un usuario."""
        try:
            return self.model.objects.get(usuario_id=usuario_id)
        except self.model.DoesNotExist:
            return None
