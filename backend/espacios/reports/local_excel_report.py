"""Genera el reporte Excel del catálogo de sedes y locales."""

from datetime import datetime

from shared.reports import ExcelReportBuilder


class LocalExcelReport:
    @staticmethod
    def generar(rows, stats: dict, *, busqueda: str = '', actor=None):
        actor_name = f"{actor.nombre} {actor.apellido}".strip() if actor else "Administrador"

        builder = ExcelReportBuilder(
            title="Reporte Ejecutivo Territorial y Sedes",
            user_name=actor_name,
            filters_text=f"Búsqueda: '{busqueda}'" if busqueda else "Todas las sedes y campus",
            sheet_name="Sedes y Campus",
        )
        builder.add_kpis([
            {"label": "Total Sedes / Locales", "value": stats['total_locales'], "tone": "info"},
            {"label": "Sedes Activas", "value": stats['locales_activos'], "tone": "success"},
            {"label": "Pabellones en Red", "value": stats['total_pabellones'], "tone": "info"},
            {"label": "Equipos en Red", "value": stats['total_equipos'], "tone": "info"},
        ])
        builder.set_columns([
            {"key": "ciudad", "label": "Ciudad", "width": 18},
            {"key": "codigo", "label": "Código Sede", "width": 16, "align": "center"},
            {"key": "nombre", "label": "Nombre de la Sede / Campus", "width": 28},
            {"key": "tipo", "label": "Tipo de Sede", "width": 16, "align": "center"},
            {"key": "cant_pabellones", "label": "Pabellones", "width": 16, "align": "center"},
            {"key": "cant_espacios", "label": "Espacios", "width": 16, "align": "center"},
            {"key": "cant_equipos", "label": "Equipos", "width": 16, "align": "center"},
            {"key": "estado", "label": "Estado", "width": 14, "align": "center"},
        ])

        builder.add_rows(rows, status_keys=['estado'])
        filename = f"reporte_territorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return builder.to_response(filename)
