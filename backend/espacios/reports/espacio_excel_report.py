"""Genera los reportes Excel del catálogo general de espacios."""

from datetime import datetime

from django.utils.text import slugify

from shared.reports import ExcelReportBuilder


class EspacioExcelReport:
    @staticmethod
    def generar_inventario(
        queryset,
        *,
        busqueda: str = '',
        tipo: str = '',
        activo: bool | None = None,
        pabellon: str = '',
        edificio: str = '',
        piso: str = '',
        ciudad: str = '',
        actor=None,
    ):
        filtro_parts = []
        if ciudad:
            filtro_parts.append(f"Ciudad: {ciudad}")
        if busqueda:
            filtro_parts.append(f"Búsqueda: '{busqueda}'")
        if tipo:
            filtro_parts.append(f"Tipo: {tipo}")
        if activo is not None:
            filtro_parts.append("Solo activos" if activo else "Solo inactivos")
        if pabellon:
            filtro_parts.append(f"Pabellón: {pabellon}")
        if edificio:
            filtro_parts.append(f"Edificio: {edificio}")
        if piso:
            filtro_parts.append(f"Piso: {piso}")
        filters_text = " | ".join(filtro_parts)
        actor_name = f"{actor.nombre} {actor.apellido}".strip() if actor else "Administrador"

        total_espacios = len(queryset)
        activos_count = sum(1 for espacio in queryset if espacio.activo)
        inactivos_count = total_espacios - activos_count
        total_equipos = sum(len(getattr(espacio, 'equipos_vigentes', [])) for espacio in queryset)

        builder = ExcelReportBuilder(
            title="Inventario General de Espacios y Ambientes",
            user_name=actor_name,
            filters_text=filters_text,
            sheet_name="Espacios",
        )
        builder.add_kpis([
            {"label": "Total Espacios", "value": total_espacios, "tone": "info"},
            {"label": "Espacios Activos", "value": activos_count, "tone": "success"},
            {
                "label": "Espacios Inactivos",
                "value": inactivos_count,
                "tone": "danger" if inactivos_count > 0 else "neutral",
            },
            {"label": "Equipos Instalados", "value": total_equipos, "tone": "info"},
        ])

        columns = [
            {"key": "codigo_espacio", "label": "Código Espacio", "width": 16, "align": "center"},
            {"key": "tipo_display", "label": "Tipo de Espacio", "width": 20},
            {"key": "sede", "label": "Sede / Local", "width": 24},
            {"key": "pabellon", "label": "Pabellón / Edificio", "width": 24},
            {"key": "piso", "label": "Piso", "width": 10, "align": "center"},
            {"key": "total_equipos", "label": "Equipos Ubicados", "width": 18, "align": "center"},
            {"key": "equipos_operativos", "label": "Operativos", "width": 14, "align": "center"},
            {"key": "equipos_falla", "label": "Con Falla / Mant.", "width": 18, "align": "center"},
            {"key": "responsables", "label": "Responsables Asignados", "width": 30},
            {"key": "estado", "label": "Estado", "width": 14, "align": "center"},
        ]
        builder.set_columns(columns)

        rows = []
        for espacio in queryset:
            local_name = (
                espacio.edificio.local.nombre
                if espacio.edificio and espacio.edificio.local
                else "—"
            )
            building_name = espacio.edificio.nombre if espacio.edificio else (espacio.pabellon or "—")
            equipment = getattr(espacio, 'equipos_vigentes', [])
            assignments = getattr(espacio, 'asignaciones_activas', [])
            responsible_names = [
                f"{assignment.usuario.nombre} {assignment.usuario.apellido}".strip()
                for assignment in assignments
                if assignment.usuario
            ]
            rows.append({
                "codigo_espacio": espacio.codigo_espacio,
                "tipo_display": espacio.get_tipo_display(),
                "sede": local_name,
                "pabellon": building_name,
                "piso": espacio.piso,
                "total_equipos": len(equipment),
                "equipos_operativos": sum(1 for equipo in equipment if equipo.estado == 'en_uso'),
                "equipos_falla": sum(
                    1 for equipo in equipment if equipo.estado in ('dañado', 'en_mantenimiento')
                ),
                "responsables": ", ".join(responsible_names) if responsible_names else "Sin asignar",
                "estado": "Activo" if espacio.activo else "Inactivo",
            })

        builder.add_rows(rows, status_keys=['estado'])
        safe_city = f"_{slugify(ciudad)}" if ciudad and ciudad.strip() else ""
        filename = f"reporte_espacios{safe_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return builder.to_response(filename)
