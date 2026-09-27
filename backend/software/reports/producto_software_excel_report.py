from datetime import datetime

from shared.reports.excel_builder import ExcelReportBuilder


def generar_reporte_productos_software(
    queryset,
    actor=None,
    busqueda: str = '',
    tipo_licencia: str = '',
):
    """Construye el reporte Excel del catálogo de productos de software."""
    filtro_parts = []
    if busqueda:
        filtro_parts.append(f"Búsqueda: '{busqueda}'")
    if tipo_licencia:
        filtro_parts.append(f"Licencia: {tipo_licencia}")
    filters_text = " | ".join(filtro_parts)
    actor_name = f"{actor.nombre} {actor.apellido}".strip() if actor else "Administrador"

    total_productos = len(queryset)
    total_licencias = sum(producto.licencias_totales for producto in queryset)
    licencias_usadas = sum(producto.licencias_usadas for producto in queryset)
    licencias_libres = sum(producto.licencias_disponibles for producto in queryset)

    builder = ExcelReportBuilder(
        title="Catálogo de Software y Licencias",
        user_name=actor_name,
        filters_text=filters_text,
        sheet_name="Software",
    )
    builder.add_kpis([
        {"label": "Total Productos", "value": total_productos, "tone": "info"},
        {"label": "Licencias Totales", "value": total_licencias, "tone": "info"},
        {
            "label": "Licencias Asignadas",
            "value": licencias_usadas,
            "tone": "warning" if licencias_usadas > 0 else "neutral",
        },
        {"label": "Licencias Libres", "value": licencias_libres, "tone": "success"},
    ])

    columns = [
        {"key": "software", "label": "Nombre del Software", "width": 28},
        {"key": "version", "label": "Versión", "width": 14, "align": "center"},
        {"key": "desarrollador", "label": "Desarrollador / Empresa", "width": 24},
        {"key": "tipo_licencia", "label": "Tipo de Licencia", "width": 18, "align": "center"},
        {"key": "licencias_totales", "label": "Total Licencias", "width": 18, "align": "center"},
        {"key": "licencias_usadas", "label": "Asignadas", "width": 16, "align": "center"},
        {"key": "licencias_disponibles", "label": "Disponibles", "width": 16, "align": "center"},
    ]
    builder.set_columns(columns)

    data = []
    for producto in queryset:
        data.append({
            "software": producto.software,
            "version": producto.version,
            "desarrollador": producto.desarrollador or "—",
            "tipo_licencia": producto.get_tipo_licencia_display(),
            "licencias_totales": producto.licencias_totales,
            "licencias_usadas": producto.licencias_usadas,
            "licencias_disponibles": producto.licencias_disponibles,
        })

    builder.add_rows(data)
    filename = f"reporte_catalogo_software_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return builder.to_response(filename)
