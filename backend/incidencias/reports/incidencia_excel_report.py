from datetime import datetime

from django.http import HttpResponse

from shared.reports import ExcelReportBuilder


def generar_reporte_excel(
    incidencias,
    stats: dict,
    *,
    busqueda: str = '',
    espacio_id: int | None = None,
    equipo_id: int | None = None,
    tipo_incidencia: str = '',
    estado: str = '',
    prioridad: str = '',
    actor=None,
) -> HttpResponse:
    """Construye la descarga Excel de las incidencias visibles."""
    filtros_aplicados = []
    if busqueda:
        filtros_aplicados.append(f'Búsqueda: "{busqueda}"')
    if tipo_incidencia:
        filtros_aplicados.append(f'Tipo: {tipo_incidencia.title()}')
    if estado:
        filtros_aplicados.append(f'Estado: {estado.replace("_", " ").title()}')
    if prioridad:
        filtros_aplicados.append(f'Prioridad: {prioridad.title()}')
    if espacio_id:
        filtros_aplicados.append(f'Espacio ID: {espacio_id}')
    if equipo_id:
        filtros_aplicados.append(f'Equipo ID: {equipo_id}')

    filtros_str = " · ".join(filtros_aplicados) if filtros_aplicados else "Todas las incidencias"
    user_name = f"{actor.nombre} {actor.apellido}".strip() if actor and hasattr(actor, 'nombre') else "Usuario KairOs"

    builder = ExcelReportBuilder(
        title="Reporte Oficial de Incidencias de Soporte",
        user_name=user_name,
        filters_text=filtros_str,
        sheet_name="Incidencias",
    )
    builder.add_kpis([
        {'label': 'Incidencias Totales', 'value': stats.get('total', 0), 'tone': 'info'},
        {'label': 'Pendientes', 'value': stats.get('pendientes', 0), 'tone': 'neutral'},
        {'label': 'En Proceso', 'value': stats.get('en_proceso', 0), 'tone': 'warning'},
        {'label': 'Resueltas', 'value': stats.get('resueltas', 0), 'tone': 'success'},
    ])

    columns = [
        {'key': 'id', 'label': 'ID', 'width': 10, 'align': 'center', 'mono': True},
        {'key': 'tipo', 'label': 'Tipo', 'width': 14, 'align': 'center'},
        {'key': 'prioridad', 'label': 'Prioridad', 'width': 14, 'align': 'center'},
        {'key': 'estado', 'label': 'Estado', 'width': 16, 'align': 'center'},
        {'key': 'equipo', 'label': 'Equipo Afectado', 'width': 20, 'mono': True},
        {'key': 'espacio', 'label': 'Espacio / Aula', 'width': 22},
        {'key': 'descripcion', 'label': 'Descripción de la Falla', 'width': 35},
        {'key': 'reportado_por', 'label': 'Reportado por', 'width': 22},
        {'key': 'asignado_a', 'label': 'Técnico Asignado', 'width': 22},
        {'key': 'fecha_reporte', 'label': 'Fecha de Reporte', 'width': 18, 'align': 'center'},
        {'key': 'fecha_resolucion', 'label': 'Fecha de Resolución', 'width': 18, 'align': 'center'},
        {'key': 'resolucion', 'label': 'Resolución / Diagnóstico', 'width': 35},
    ]
    builder.set_columns(columns)

    rows = []
    for inc in incidencias:
        eq_desc = f"{inc.equipo.codigo} ({inc.equipo.marca} {inc.equipo.modelo})" if inc.equipo else "—"
        esp_desc = f"{inc.espacio.codigo_espacio} · {inc.espacio.pabellon}" if inc.espacio else "—"
        rep_desc = f"{inc.reportado_por.nombre} {inc.reportado_por.apellido}".strip() if inc.reportado_por else "—"
        asig_desc = f"{inc.asignado_a.nombre} {inc.asignado_a.apellido}".strip() if inc.asignado_a else "Sin asignar"
        f_rep = inc.created_at.strftime("%d/%m/%Y %H:%M") if inc.created_at else "—"
        f_res = inc.fecha_resolucion.strftime("%d/%m/%Y %H:%M") if inc.fecha_resolucion else "—"
        rows.append({
            'id': inc.id,
            'tipo': (
                inc.get_tipo_incidencia_display()
                if hasattr(inc, 'get_tipo_incidencia_display') else inc.tipo_incidencia
            ),
            'prioridad': inc.prioridad,
            'estado': inc.estado,
            'equipo': eq_desc,
            'espacio': esp_desc,
            'descripcion': inc.descripcion,
            'reportado_por': rep_desc,
            'asignado_a': asig_desc,
            'fecha_reporte': f_rep,
            'fecha_resolucion': f_res,
            'resolucion': inc.resolucion or inc.motivo_cierre or "—",
        })

    builder.add_rows(rows, status_keys=['estado', 'prioridad'])
    filename = f"reporte_incidencias_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return builder.to_response(filename)
