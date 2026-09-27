from datetime import datetime

from django.http import HttpResponse

from shared.reports import ExcelReportBuilder


def generar_reporte_usuarios(
    usuarios,
    kpis: list[dict],
    actor,
    busqueda: str = '',
    rol: str = '',
    activo: bool | None = None,
    local_id: int | None = None,
) -> HttpResponse:
    """Construye el reporte Excel de usuarios filtrados."""
    filtros_aplicados = []
    if busqueda:
        filtros_aplicados.append(f'Búsqueda: "{busqueda}"')
    if rol:
        filtros_aplicados.append(f'Rol: {rol.title()}')
    if activo is not None:
        filtros_aplicados.append(f'Estado: {"Activo" if activo else "Inactivo"}')
    if local_id:
        filtros_aplicados.append(f'Local ID: {local_id}')

    filtros_str = " · ".join(filtros_aplicados) if filtros_aplicados else "Todos los usuarios"
    user_name = (
        f"{actor.nombre} {actor.apellido}".strip()
        if actor and hasattr(actor, 'nombre')
        else "Usuario KairOs"
    )

    builder = ExcelReportBuilder(
        title="Reporte Oficial de Cuentas de Usuario",
        user_name=user_name,
        filters_text=filtros_str,
        sheet_name="Usuarios",
    )

    builder.add_kpis(kpis)

    columns = [
        {'key': 'id', 'label': 'ID', 'width': 10, 'align': 'center', 'mono': True},
        {'key': 'nombre_completo', 'label': 'Nombre Completo', 'width': 26},
        {'key': 'username', 'label': 'Usuario', 'width': 18, 'mono': True},
        {'key': 'correo', 'label': 'Correo Institucional', 'width': 28},
        {'key': 'dni', 'label': 'DNI', 'width': 14, 'align': 'center', 'mono': True},
        {'key': 'telefono', 'label': 'Teléfono', 'width': 16, 'align': 'center'},
        {'key': 'rol', 'label': 'Rol Asignado', 'width': 16, 'align': 'center'},
        {'key': 'supervisor', 'label': 'Supervisor Directo', 'width': 24},
        {'key': 'is_active', 'label': 'Estado', 'width': 14, 'align': 'center'},
        {'key': 'fecha_registro', 'label': 'Fecha de Registro', 'width': 18, 'align': 'center'},
    ]
    builder.set_columns(columns)

    rows = []
    for usuario in usuarios:
        supervisor = (
            f"{usuario.supervisor.nombre} {usuario.supervisor.apellido}".strip()
            if usuario.supervisor
            else "Sin supervisor"
        )
        fecha_registro = (
            usuario.created_at.strftime("%d/%m/%Y")
            if hasattr(usuario, 'created_at') and usuario.created_at
            else "—"
        )
        rows.append({
            'id': usuario.id,
            'nombre_completo': f"{usuario.nombre} {usuario.apellido}".strip(),
            'username': usuario.username,
            'correo': usuario.correo,
            'dni': usuario.dni or "—",
            'telefono': usuario.telefono or "—",
            'rol': usuario.get_rol_display() if hasattr(usuario, 'get_rol_display') else usuario.rol,
            'supervisor': supervisor,
            'is_active': "Activo" if usuario.is_active else "Inactivo",
            'fecha_registro': fecha_registro,
        })

    builder.add_rows(rows, status_keys=['is_active'])
    filename = f"reporte_usuarios_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return builder.to_response(filename)
