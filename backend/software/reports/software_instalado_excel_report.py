from datetime import datetime

from shared.reports.excel_builder import ExcelReportBuilder


def generar_reporte_software_instalado(
    queryset,
    actor=None,
    busqueda: str = '',
    equipo_id: int | None = None,
    espacio_id: int | None = None,
    producto_software_id: int | None = None,
):
    """Construye el reporte Excel de instalaciones de software."""
    filtro_parts = []
    if busqueda:
        filtro_parts.append(f"Búsqueda: '{busqueda}'")
    if equipo_id:
        filtro_parts.append(f"Equipo ID: {equipo_id}")
    if espacio_id:
        filtro_parts.append(f"Espacio ID: {espacio_id}")
    if producto_software_id:
        filtro_parts.append(f"Producto ID: {producto_software_id}")
    filters_text = " | ".join(filtro_parts)
    actor_name = f"{actor.nombre} {actor.apellido}".strip() if actor else "Administrador"

    total_instalaciones = len(queryset)
    equipos_count = len(set(instalacion.equipo_id for instalacion in queryset))
    productos_count = len(set(instalacion.producto_software_id for instalacion in queryset))

    builder = ExcelReportBuilder(
        title="Inventario de Software Instalado por Estación",
        user_name=actor_name,
        filters_text=filters_text,
        sheet_name="Instalaciones",
    )
    builder.add_kpis([
        {"label": "Total Instalaciones", "value": total_instalaciones, "tone": "info"},
        {"label": "Equipos con Software", "value": equipos_count, "tone": "info"},
        {"label": "Productos Distintos", "value": productos_count, "tone": "success"},
    ])

    columns = [
        {"key": "codigo_equipo", "label": "Código Equipo", "width": 18, "align": "center"},
        {"key": "espacio", "label": "Espacio / Ubicación", "width": 22},
        {"key": "software", "label": "Software Instalado", "width": 28},
        {"key": "version", "label": "Versión", "width": 14, "align": "center"},
        {"key": "tipo_licencia", "label": "Tipo de Licencia", "width": 18, "align": "center"},
        {"key": "numero_licencia", "label": "N° de Licencia / Clave", "width": 24, "align": "center", "mono": True},
        {"key": "fecha_instalacion", "label": "Fecha Instalación", "width": 18, "align": "center"},
    ]
    builder.set_columns(columns)

    data = []
    for instalacion in queryset:
        espacio_nombre = (
            instalacion.equipo.espacio.codigo_espacio
            if instalacion.equipo and instalacion.equipo.espacio
            else "Sin espacio"
        )
        producto = instalacion.producto_software
        data.append({
            "codigo_equipo": instalacion.equipo.codigo if instalacion.equipo else "—",
            "espacio": espacio_nombre,
            "software": producto.software if producto else "—",
            "version": producto.version if producto else "—",
            "tipo_licencia": producto.get_tipo_licencia_display() if producto else "—",
            "numero_licencia": instalacion.numero_licencia or "—",
            "fecha_instalacion": instalacion.fecha_instalacion,
        })

    builder.add_rows(data)
    filename = f"reporte_instalaciones_software_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return builder.to_response(filename)
