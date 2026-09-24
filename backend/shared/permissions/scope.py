from django.db.models import Q

from espacios.models import EspacioUsuario


OPERATIONAL_ROLES = {'tecnico', 'responsable'}
FULL_SCOPE_ROLES = {'admin', 'superadmin'}
REPORTER_ROLES = {'docente', 'usuario'}


def get_accessible_space_ids(actor):
    """
    Retorna el conjunto de espacios que el actor puede operar.

    Administradores y superadministradores no tienen restricción territorial.
    Los demás roles operativos heredan el alcance de sus asignaciones activas
    en sede, edificio, piso o espacio. Los roles reportantes no reciben un
    alcance operativo porque solo deben consultar sus propios reportes.
    """
    if actor is None or not getattr(actor, 'is_authenticated', False):
        return set()

    if actor.rol in FULL_SCOPE_ROLES or getattr(actor, 'is_superuser', False):
        return None

    if actor.rol in REPORTER_ROLES:
        return set()

    assignments = EspacioUsuario.objects.filter(
        usuario_id=actor.id,
        activo=True,
        is_deleted=False,
    ).values('ambito', 'local_id', 'edificio_id', 'piso', 'espacio_id')

    scope_filter = Q(pk__in=[])
    for assignment in assignments:
        ambito = assignment['ambito']
        if ambito == EspacioUsuario.AMBITO_ESPACIO and assignment['espacio_id']:
            scope_filter |= Q(pk=assignment['espacio_id'])
        elif ambito == EspacioUsuario.AMBITO_PISO and assignment['edificio_id']:
            scope_filter |= Q(
                edificio_id=assignment['edificio_id'],
                piso=str(assignment['piso']),
            )
        elif ambito == EspacioUsuario.AMBITO_EDIFICIO and assignment['edificio_id']:
            scope_filter |= Q(edificio_id=assignment['edificio_id'])
        elif ambito == EspacioUsuario.AMBITO_SEDE and assignment['local_id']:
            scope_filter |= Q(edificio__local_id=assignment['local_id'])

    # Compatibilidad con asignaciones de sede anteriores al modelo jerárquico.
    legacy_local_ids = actor.usuario_sedes.filter(
        activo=True,
        is_deleted=False,
    ).values_list('local_id', flat=True)
    scope_filter |= Q(edificio__local_id__in=legacy_local_ids)

    from espacios.models import Espacio
    return set(Espacio.objects.filter(scope_filter, is_deleted=False).values_list('id', flat=True))
