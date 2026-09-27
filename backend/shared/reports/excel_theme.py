"""Colores y tonos reutilizables para reportes Excel de KairOs."""


class ExcelTheme:
    COLOR_NAVY_DARK = "17264D"
    COLOR_NAVY_LIGHT = "1C2B3E"
    COLOR_PRIMARY_BLUE = "488DFE"
    COLOR_PRIMARY_BG = "EFF6FF"
    COLOR_WHITE = "FFFFFF"
    COLOR_ZEBRA = "F8FAFC"
    COLOR_BORDER = "CBD5E1"
    COLOR_TEXT_MAIN = "0F172A"
    COLOR_TEXT_MUTED = "64748B"

    STATUS_PALETTES = {
        'success': {'fill': 'D1FAE5', 'font': '065F46'},
        'warning': {'fill': 'FEF3C7', 'font': '92400E'},
        'danger': {'fill': 'FEE2E2', 'font': '991B1B'},
        'info': {'fill': 'DBEAFE', 'font': '1E40AF'},
        'neutral': {'fill': 'F1F5F9', 'font': '334155'},
    }

    STATUS_MAP = {
        'en_uso': 'success',
        'operativo': 'success',
        'en_mantenimiento': 'warning',
        'dañado': 'danger',
        'de_baja': 'danger',
        'pendiente': 'neutral',
        'en_proceso': 'warning',
        'resuelto': 'success',
        'cerrado': 'success',
        'cancelado': 'danger',
        'duplicado': 'neutral',
        'baja': 'neutral',
        'media': 'info',
        'alta': 'warning',
        'critica': 'danger',
        'activo': 'success',
        'inactivo': 'danger',
        'true': 'success',
        'false': 'danger',
    }
