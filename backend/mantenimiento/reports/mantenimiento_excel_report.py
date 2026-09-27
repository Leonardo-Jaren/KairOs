from datetime import datetime

from django.http import HttpResponse

from shared.reports import ExcelReportBuilder


def generar_reporte_excel(
    mantenimientos,
    stats: dict,
    *,
    busqueda: str = '',
    estado: str = '',
    tipo_mantenimiento: str = '',
    equipo_id: int | None = None,
    actor=None,
) -> HttpResponse:
    """Construye la descarga Excel de las órdenes de mantenimiento."""
    filtros_aplicados = []
    if busqueda:
        filtros_aplicados.append(f'Búsqueda: "{busqueda}"')
    if tipo_mantenimiento:
        filtros_aplicados.append(f'Tipo: {tipo_mantenimiento.title()}')
    if estado:
        filtros_aplicados.append(f'Estado: {estado.replace("_", " ").title()}')
    if equipo_id:
        filtros_aplicados.append(f'Equipo ID: {equipo_id}')

    filtros_str = " · ".join(filtros_aplicados) if filtros_aplicados else "Todas las órdenes de mantenimiento"
    user_name = f"{actor.nombre} {actor.apellido}".strip() if actor and hasattr(actor, 'nombre') else "Usuario KairOs"

    builder = ExcelReportBuilder(
        title="Reporte Oficial de Mantenimiento de Hardware",
        user_name=user_name,
        filters_text=filtros_str,
        sheet_name="Mantenimiento",
    )
    builder.add_kpis([
        {'label': 'Total Órdenes', 'value': stats.get('total', 0), 'tone': 'info'},
        {'label': 'Pendientes', 'value': stats.get('pendientes', 0), 'tone': 'neutral'},
        {'label': 'En Proceso', 'value': stats.get('en_proceso', 0), 'tone': 'warning'},
        {'label': 'Finalizados', 'value': stats.get('resueltos', 0), 'tone': 'success'},
    ])

    columns = [
        {'key': 'id', 'label': 'ID Orden', 'width': 12, 'align': 'center', 'mono': True},
        {'key': 'tipo', 'label': 'Tipo', 'width': 14, 'align': 'center'},
        {'key': 'estado', 'label': 'Estado', 'width': 16, 'align': 'center'},
        {'key': 'resultado_equipo', 'label': 'Resultado Equipo', 'width': 16, 'align': 'center'},
        {'key': 'equipo', 'label': 'Equipo Intervenido', 'width': 22, 'mono': True},
        {'key': 'espacio', 'label': 'Ubicación / Espacio', 'width': 22},
        {'key': 'incidencia', 'label': 'Origen Incidencia', 'width': 18, 'align': 'center'},
        {'key': 'tecnicos', 'label': 'Técnico(s) Responsable(s)', 'width': 26},
        {'key': 'fecha_programada', 'label': 'Fecha Programada', 'width': 16, 'align': 'center'},
        {'key': 'fecha_inicio', 'label': 'Fecha Inicio', 'width': 18, 'align': 'center'},
        {'key': 'fecha_fin', 'label': 'Fecha Fin', 'width': 18, 'align': 'center'},
        {'key': 'descripcion', 'label': 'Descripción de la Orden', 'width': 35},
        {'key': 'diagnostico', 'label': 'Diagnóstico Técnico', 'width': 35},
        {'key': 'trabajo_realizado', 'label': 'Trabajo Realizado', 'width': 35},
        {'key': 'prueba_realizada', 'label': 'Prueba de Funcionamiento', 'width': 18, 'align': 'center'},
    ]
    builder.set_columns(columns)

    rows = []
    for mantenimiento in mantenimientos:
        eq_desc = (
            f"{mantenimiento.equipo.codigo} "
            f"({mantenimiento.equipo.marca} {mantenimiento.equipo.modelo})"
            if mantenimiento.equipo else "—"
        )
        espacio = mantenimiento.equipo.espacio if mantenimiento.equipo else None
        esp_desc = f"{espacio.codigo_espacio} · {espacio.pabellon}" if espacio else "Sin espacio"
        inc_desc = f"INC-{mantenimiento.incidencia_origen.id}" if mantenimiento.incidencia_origen else "Independiente"
        tecs_desc = ", ".join(
            [f"{tecnico.nombre} {tecnico.apellido}".strip() for tecnico in mantenimiento.tecnicos.all()]
        ) if mantenimiento.tecnicos.exists() else "Sin asignar"

        f_ini = mantenimiento.fecha_inicio.strftime("%d/%m/%Y %H:%M") if mantenimiento.fecha_inicio else "—"
        f_fin = mantenimiento.fecha_fin.strftime("%d/%m/%Y %H:%M") if mantenimiento.fecha_fin else "—"
        rows.append({
            'id': f"MNT-{mantenimiento.id}",
            'tipo': (
                mantenimiento.get_tipo_mantenimiento_display()
                if hasattr(mantenimiento, 'get_tipo_mantenimiento_display')
                else mantenimiento.tipo_mantenimiento
            ),
            'estado': mantenimiento.estado,
            'resultado_equipo': (
                mantenimiento.get_resultado_equipo_display()
                if hasattr(mantenimiento, 'get_resultado_equipo_display') and mantenimiento.resultado_equipo
                else (mantenimiento.resultado_equipo or "—")
            ),
            'equipo': eq_desc,
            'espacio': esp_desc,
            'incidencia': inc_desc,
            'tecnicos': tecs_desc,
            'fecha_programada': mantenimiento.fecha,
            'fecha_inicio': f_ini,
            'fecha_fin': f_fin,
            'descripcion': mantenimiento.descripcion,
            'diagnostico': mantenimiento.diagnostico or "—",
            'trabajo_realizado': mantenimiento.trabajo_realizado or "—",
            'prueba_realizada': "Realizada y aprobada" if mantenimiento.prueba_realizada else "Pendiente",
        })

    builder.add_rows(rows, status_keys=['estado', 'resultado_equipo'])
    filename = f"reporte_mantenimiento_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return builder.to_response(filename)
