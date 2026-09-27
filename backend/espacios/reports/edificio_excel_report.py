"""Renderiza los reportes Excel de pabellones y pisos."""

from datetime import datetime

from shared.reports import ExcelReportBuilder


class EdificioExcelReport:
    @staticmethod
    def generar_catalogo(local, rows, stats: dict, *, actor=None):
        local_suffix = f" - {local.nombre}" if local else ""
        actor_name = f"{actor.nombre} {actor.apellido}".strip() if actor else "Administrador"
        builder = ExcelReportBuilder(
            title=f"Reporte de Pabellones e Infraestructura{local_suffix}",
            user_name=actor_name,
            filters_text=f"Sede: {local.nombre}" if local else "Todos los pabellones",
            sheet_name="Pabellones",
        )
        builder.add_kpis([
            {"label": "Total Pabellones", "value": stats['total_pabellones'], "tone": "info"},
            {"label": "Total Ambientes", "value": stats['total_ambientes'], "tone": "info"},
            {"label": "Laboratorios", "value": stats['total_laboratorios'], "tone": "success"},
            {"label": "Equipos Instalados", "value": stats['total_equipos'], "tone": "info"},
        ])
        builder.set_columns([
            {"key": "sede", "label": "Sede / Local", "width": 24},
            {"key": "codigo", "label": "Código Pabellón", "width": 18, "align": "center"},
            {"key": "nombre", "label": "Nombre Pabellón", "width": 28},
            {"key": "pisos", "label": "Pisos con Ambientes", "width": 18, "align": "center"},
            {"key": "espacios", "label": "Total Ambientes", "width": 16, "align": "center"},
            {"key": "laboratorios", "label": "Laboratorios", "width": 16, "align": "center"},
            {"key": "aulas", "label": "Aulas", "width": 14, "align": "center"},
            {"key": "equipos", "label": "Equipos", "width": 14, "align": "center"},
            {"key": "estado", "label": "Estado", "width": 14, "align": "center"},
        ])
        builder.add_rows(rows, status_keys=['estado'])
        filename = f"reporte_pabellones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return builder.to_response(filename)

    @staticmethod
    def generar_reporte_piso(building, floor: str, rows, stats: dict, *, actor=None):
        local_name = building.local.nombre if building.local else "—"
        actor_name = f"{actor.nombre} {actor.apellido}".strip() if actor else "Administrador"
        builder = ExcelReportBuilder(
            title=f"Reporte Técnico de Planta - {building.nombre} (Piso {floor})",
            subtitle=f"Croquis y Ambientes Operativos · Sede {local_name}",
            user_name=actor_name,
            filters_text=f"Pabellón: {building.nombre} | Piso: {floor}",
            sheet_name=f"Pabellón {building.codigo} Piso {floor}",
        )
        maintenance_count = stats['equipos_mantenimiento']
        damaged_count = stats['equipos_dañados']
        builder.add_kpis([
            {"label": "Ambientes en Piso", "value": stats['total_ambientes'], "tone": "info"},
            {"label": "Equipos en Piso", "value": stats['total_equipos'], "tone": "info"},
            {"label": "Equipos Operativos", "value": stats['equipos_operativos'], "tone": "success"},
            {
                "label": "En Mantenimiento",
                "value": maintenance_count,
                "tone": "warning" if maintenance_count > 0 else "neutral",
            },
            {
                "label": "Con Falla / Dañados",
                "value": damaged_count,
                "tone": "danger" if damaged_count > 0 else "neutral",
            },
        ])
        builder.set_columns([
            {"key": "codigo_espacio", "label": "Código Ambiente", "width": 18, "align": "center"},
            {"key": "tipo", "label": "Tipo de Ambiente", "width": 18},
            {"key": "equipos_operativos", "label": "Operativos", "width": 14, "align": "center"},
            {"key": "equipos_mantenimiento", "label": "En Mantenimiento", "width": 18, "align": "center"},
            {"key": "equipos_dañados", "label": "Con Falla", "width": 14, "align": "center"},
            {"key": "total_equipos", "label": "Total Equipos", "width": 16, "align": "center"},
            {"key": "responsables", "label": "Personal Asignado", "width": 30},
            {"key": "estado", "label": "Estado", "width": 14, "align": "center"},
        ])
        builder.add_rows(rows, status_keys=['estado'])
        filename = f"reporte_piso_{building.codigo}_p{floor}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return builder.to_response(filename)
