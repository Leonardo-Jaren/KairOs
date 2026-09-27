from datetime import datetime

from django.http import HttpResponse

from shared.reports import ExcelReportBuilder


def generar_reporte_excel(
    equipos,
    stats: dict,
    *,
    busqueda: str = '',
    tipo_equipo: str = '',
    estado: str = '',
    espacio_id: int | None = None,
    actor=None,
) -> HttpResponse:
    """Construye la descarga Excel del inventario de equipos."""
    filtros_aplicados = []
    if busqueda:
        filtros_aplicados.append(f'Búsqueda: "{busqueda}"')
    if tipo_equipo:
        filtros_aplicados.append(f'Tipo: {tipo_equipo.title()}')
    if estado:
        filtros_aplicados.append(f'Estado: {estado.replace("_", " ").title()}')
    if espacio_id:
        filtros_aplicados.append(f'Espacio ID: {espacio_id}')

    filtros_str = " · ".join(filtros_aplicados) if filtros_aplicados else "Todos los equipos"
    user_name = f"{actor.nombre} {actor.apellido}".strip() if actor and hasattr(actor, 'nombre') else "Administrador"

    builder = ExcelReportBuilder(
        title="Reporte Oficial de Inventario de Equipos",
        user_name=user_name,
        filters_text=filtros_str,
        sheet_name="Equipos",
    )
    builder.add_kpis([
        {'label': 'Total Equipos', 'value': stats.get('total', 0), 'tone': 'info'},
        {'label': 'En Uso', 'value': stats.get('en_uso', 0), 'tone': 'success'},
        {'label': 'En Mantenimiento', 'value': stats.get('en_mantenimiento', 0), 'tone': 'warning'},
        {'label': 'De Baja', 'value': stats.get('de_baja', 0), 'tone': 'danger'},
    ])

    columns = [
        {'key': 'codigo', 'label': 'Código Interno', 'width': 16, 'align': 'center', 'mono': True},
        {'key': 'tipo_equipo', 'label': 'Tipo', 'width': 14, 'align': 'center'},
        {'key': 'marca', 'label': 'Marca', 'width': 16},
        {'key': 'modelo', 'label': 'Modelo', 'width': 18},
        {'key': 'numero_serie', 'label': 'N° Serie', 'width': 18, 'mono': True},
        {'key': 'numero_mac', 'label': 'Dirección MAC', 'width': 18, 'mono': True},
        {'key': 'ipv4', 'label': 'IPv4', 'width': 16, 'mono': True},
        {'key': 'espacio', 'label': 'Espacio Asignado', 'width': 22},
        {'key': 'estado', 'label': 'Estado', 'width': 16, 'align': 'center'},
        {'key': 'modo_adquisicion', 'label': 'Adquisición', 'width': 14, 'align': 'center'},
        {'key': 'fecha_adquisicion', 'label': 'Fecha Adquisición', 'width': 16, 'align': 'center'},
        {'key': 'responsable', 'label': 'Responsable', 'width': 22},
    ]
    builder.set_columns(columns)

    rows = []
    for eq in equipos:
        espacio_desc = f"{eq.espacio.codigo_espacio} ({eq.espacio.pabellon})" if eq.espacio else "Sin asignar"
        resp_desc = (
            f"{eq.responsable_usuario.nombre} {eq.responsable_usuario.apellido}".strip()
            if eq.responsable_usuario else "Sin responsable"
        )
        rows.append({
            'codigo': eq.codigo,
            'tipo_equipo': (
                eq.get_tipo_equipo_display()
                if hasattr(eq, 'get_tipo_equipo_display') else eq.tipo_equipo
            ),
            'marca': eq.marca,
            'modelo': eq.modelo,
            'numero_serie': eq.numero_serie,
            'numero_mac': eq.numero_mac or "—",
            'ipv4': eq.ipv4 or "—",
            'espacio': espacio_desc,
            'estado': eq.estado,
            'modo_adquisicion': (
                eq.get_modo_adquisicion_display()
                if hasattr(eq, 'get_modo_adquisicion_display') else eq.modo_adquisicion
            ),
            'fecha_adquisicion': eq.fecha_adquisicion,
            'responsable': resp_desc,
        })

    builder.add_rows(rows, status_keys=['estado'])
    filename = f"reporte_equipos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return builder.to_response(filename)
