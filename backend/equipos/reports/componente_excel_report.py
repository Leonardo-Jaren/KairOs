from datetime import datetime

from django.http import HttpResponse

from shared.reports.excel_builder import ExcelReportBuilder


def generar_reporte_excel(
    componentes,
    *,
    equipo_filtro=None,
    equipo_id: int | None = None,
    busqueda: str = '',
    tipo: str = '',
    actor=None,
) -> HttpResponse:
    """Construye la descarga Excel del inventario de componentes."""
    filtro_parts = []
    if equipo_id and equipo_filtro:
        filtro_parts.append(f"Equipo: {equipo_filtro.codigo}")
    if busqueda:
        filtro_parts.append(f"Búsqueda: '{busqueda}'")
    if tipo:
        filtro_parts.append(f"Tipo: {tipo}")
    filters_text = " | ".join(filtro_parts)

    actor_name = f"{actor.nombre} {actor.apellido}".strip() if actor else "Administrador"

    total_componentes = len(componentes)
    equipos_distintos = len(set(c.equipo_id for c in componentes))
    tipos_distintos = len(set(c.tipo for c in componentes))

    builder = ExcelReportBuilder(
        title="Inventario de Componentes de Hardware",
        user_name=actor_name,
        filters_text=filters_text,
        sheet_name="Componentes",
    )
    builder.add_kpis([
        {"label": "Total Componentes", "value": total_componentes, "tone": "info"},
        {"label": "Equipos con Hardware", "value": equipos_distintos, "tone": "info"},
        {"label": "Tipos Distintos", "value": tipos_distintos, "tone": "success"},
    ])

    columns = [
        {"key": "codigo_equipo", "label": "Código Equipo", "width": 18, "align": "center"},
        {"key": "tipo_display", "label": "Tipo de Componente", "width": 20},
        {"key": "modelo", "label": "Modelo / Referencia", "width": 24},
        {"key": "descripcion", "label": "Especificaciones / Detalle", "width": 38},
        {"key": "estado_equipo", "label": "Estado del Equipo", "width": 18, "align": "center"},
    ]
    builder.set_columns(columns)

    rows = []
    for comp in componentes:
        rows.append({
            "codigo_equipo": comp.equipo.codigo if comp.equipo else "—",
            "tipo_display": comp.get_tipo_display(),
            "modelo": comp.modelo,
            "descripcion": comp.descripcion or "—",
            "estado_equipo": comp.equipo.get_estado_display() if comp.equipo else "—",
        })

    builder.add_rows(rows, status_keys=['estado_equipo'])
    filename = f"reporte_componentes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return builder.to_response(filename)
