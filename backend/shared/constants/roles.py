ROL_SUPERADMIN  = 'superadmin'
ROL_ADMIN       = 'admin'
ROL_RESPONSABLE = 'responsable'
ROL_TECNICO     = 'tecnico'
ROL_DOCENTE     = 'docente'
ROL_USUARIO     = 'usuario'

ROLES = [
    (ROL_SUPERADMIN,  'Superadministrador'),
    (ROL_ADMIN,       'Administrador'),
    (ROL_RESPONSABLE, 'Responsable de Sede / Área'),
    (ROL_TECNICO,     'Técnico'),
    (ROL_DOCENTE,     'Docente'),
    (ROL_USUARIO,     'Usuario'),
]

MODULOS_SISTEMA = [
    ('espacios', 'Espacios'),
    ('equipos', 'Equipos'),
    ('mantenimiento', 'Mantenimiento'),
    ('incidencias', 'Incidencias'),
    ('software', 'Software'),
    ('usuarios', 'Usuarios'),
    ('auditoria', 'Auditoría'),
]

ACCIONES_SISTEMA = ['ver', 'crear', 'editar', 'eliminar']

ROL_PERMISOS_BASE = {
    ROL_SUPERADMIN: {
        'espacios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'equipos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'mantenimiento': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'incidencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'software': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'usuarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'auditoria': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
    },
    ROL_ADMIN: {
        'espacios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'equipos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'mantenimiento': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'incidencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'software': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'usuarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'auditoria': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
    },
    ROL_RESPONSABLE: {
        'espacios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'equipos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'mantenimiento': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'incidencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        'software': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'usuarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'auditoria': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
    },
    ROL_TECNICO: {
        'espacios': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
        'equipos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'mantenimiento': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'incidencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'software': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'usuarios': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
        'auditoria': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
    },
    ROL_DOCENTE: {
        'espacios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
        'equipos': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
        'mantenimiento': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
        'incidencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'software': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
        'usuarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
        'auditoria': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
    },
    ROL_USUARIO: {
        'espacios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
        'equipos': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
        'mantenimiento': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
        'incidencias': {'ver': True, 'crear': True, 'editar': False, 'eliminar': False},
        'software': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
        'usuarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
        'auditoria': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
    },
}
