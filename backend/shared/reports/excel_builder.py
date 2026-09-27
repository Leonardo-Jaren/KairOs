"""Fachada fluida que coordina la creación de reportes Excel."""

from typing import Any

import openpyxl

from .excel_header_renderer import ExcelHeaderRenderer
from .excel_response import ExcelResponseFactory
from .excel_table_renderer import ExcelTableRenderer
from .excel_theme import ExcelTheme


class ExcelReportBuilder:
    """Mantiene la interfaz fluida y delega cada parte del renderizado."""

    COLOR_NAVY_DARK = ExcelTheme.COLOR_NAVY_DARK
    COLOR_NAVY_LIGHT = ExcelTheme.COLOR_NAVY_LIGHT
    COLOR_PRIMARY_BLUE = ExcelTheme.COLOR_PRIMARY_BLUE
    COLOR_PRIMARY_BG = ExcelTheme.COLOR_PRIMARY_BG
    COLOR_WHITE = ExcelTheme.COLOR_WHITE
    COLOR_ZEBRA = ExcelTheme.COLOR_ZEBRA
    COLOR_BORDER = ExcelTheme.COLOR_BORDER
    COLOR_TEXT_MAIN = ExcelTheme.COLOR_TEXT_MAIN
    COLOR_TEXT_MUTED = ExcelTheme.COLOR_TEXT_MUTED
    STATUS_PALETTES = ExcelTheme.STATUS_PALETTES
    STATUS_MAP = ExcelTheme.STATUS_MAP

    def __init__(
        self,
        title: str,
        subtitle: str = "Sistema de Gestión Tecnológica e Infraestructura KairOs",
        user_name: str = "",
        filters_text: str = "",
        sheet_name: str = "Reporte",
    ):
        self.workbook = openpyxl.Workbook()
        self.current_sheet = self.workbook.active
        self.current_sheet.title = sheet_name
        self.title = title
        self.subtitle = subtitle
        self.user_name = user_name
        self.filters_text = filters_text
        self.current_row = 1
        self.columns_config: list[dict[str, Any]] = []
        self.data_start_row = 1
        self.header_row = 1

        self.current_sheet.views.sheetView[0].showGridLines = True
        self._set_renderers()
        self.current_row = self._header_renderer.render_header()

    def _set_renderers(self) -> None:
        self._header_renderer = ExcelHeaderRenderer(
            self.current_sheet,
            self.title,
            self.user_name,
            self.filters_text,
        )
        self._table_renderer = ExcelTableRenderer(self.current_sheet)

    def add_sheet(self, sheet_name: str) -> "ExcelReportBuilder":
        self.current_sheet = self.workbook.create_sheet(title=sheet_name)
        self.current_sheet.views.sheetView[0].showGridLines = True
        self.columns_config = []
        self.data_start_row = 1
        self.header_row = 1
        self._set_renderers()
        self.current_row = self._header_renderer.render_header()
        return self

    def add_kpis(self, kpi_list: list[dict[str, Any]]) -> "ExcelReportBuilder":
        self.current_row = self._header_renderer.add_kpis(self.current_row, kpi_list)
        return self

    def set_columns(self, columns: list[dict[str, Any]]) -> "ExcelReportBuilder":
        self.columns_config = columns
        self.header_row, self.data_start_row = self._table_renderer.set_columns(
            columns,
            self.current_row,
        )
        self.current_row = self.data_start_row
        return self

    def add_rows(
        self,
        data: list[dict[str, Any]],
        status_keys: list[str] | None = None,
    ) -> "ExcelReportBuilder":
        self.current_row = self._table_renderer.add_rows(
            data,
            self.current_row,
            status_keys,
        )
        return self

    def to_bytes(self) -> bytes:
        return ExcelResponseFactory.to_bytes(self.workbook)

    def to_response(self, filename: str):
        return ExcelResponseFactory.to_response(self.workbook, filename)
