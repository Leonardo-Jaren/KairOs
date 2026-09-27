import json

from django.http import HttpResponse

from shared.reports.excel_builder import ExcelReportBuilder


def generar_reporte_historial(
    eventos,
    actor=None,
    modulo: str | None = None,
    tipo_evento: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
) -> HttpResponse:
    """Construye el reporte Excel de auditoría y trazabilidad."""
    modulos_distintos = len(set(evento.content_type.model for evento in eventos if evento.content_type))
    usuarios_distintos = len(set(evento.usuario_id for evento in eventos if evento.usuario_id))
    actor_name = f"{actor.nombre} {actor.apellido}".strip() if actor else "Sistema KairOs"

    filtro_parts = []
    if modulo:
        filtro_parts.append(f"Módulo: {modulo}")
    if tipo_evento:
        filtro_parts.append(f"Tipo: {tipo_evento}")
    if fecha_desde:
        filtro_parts.append(f"Desde: {fecha_desde}")
    if fecha_hasta:
        filtro_parts.append(f"Hasta: {fecha_hasta}")
    filters_text = " | ".join(filtro_parts)

    builder = ExcelReportBuilder(
        title="Registro de Auditoría y Trazabilidad del Sistema",
        subtitle="KairOs IT Asset Management — Pistas de Auditoría Globales",
        user_name=actor_name,
        filters_text=filters_text,
        sheet_name="Log Auditoría",
    )
    builder.add_kpis([
        {"label": "Total Eventos", "value": len(eventos), "tone": "info"},
        {"label": "Módulos Auditados", "value": modulos_distintos, "tone": "neutral"},
        {"label": "Usuarios Activos", "value": usuarios_distintos, "tone": "success"},
    ])

    columns = [
        {"key": "id", "label": "ID", "width": 8, "align": "center"},
        {"key": "fecha", "label": "Fecha y Hora", "width": 18, "align": "center"},
        {"key": "modulo", "label": "Módulo", "width": 16, "align": "center"},
        {"key": "object_id", "label": "ID Objeto", "width": 12, "align": "center"},
        {"key": "tipo_evento", "label": "Tipo de Evento", "width": 24},
        {"key": "descripcion", "label": "Descripción", "width": 36},
        {"key": "usuario", "label": "Usuario Responsable", "width": 24},
        {"key": "rol", "label": "Rol", "width": 14, "align": "center"},
        {"key": "datos_extra", "label": "Datos Adicionales", "width": 32},
    ]
    builder.set_columns(columns)

    data = []
    for evento in eventos:
        usuario_str = (
            evento.usuario.get_full_name() or evento.usuario.username
            if evento.usuario
            else 'Sistema'
        )
        rol_str = getattr(evento.usuario, 'rol', '—').upper() if evento.usuario else '—'
        modulo_str = evento.content_type.model.title() if evento.content_type else '—'
        datos_str = json.dumps(evento.datos_extra, ensure_ascii=False) if evento.datos_extra else '—'
        data.append({
            "id": evento.id,
            "fecha": evento.fecha.strftime('%Y-%m-%d %H:%M') if evento.fecha else '—',
            "modulo": modulo_str,
            "object_id": evento.object_id,
            "tipo_evento": evento.tipo_evento,
            "descripcion": evento.descripcion,
            "usuario": usuario_str,
            "rol": rol_str,
            "datos_extra": datos_str,
        })

    builder.add_rows(data)
    return builder.to_response("reporte_auditoria_historial.xlsx")
