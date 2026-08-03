from datetime import date


def parse_boolean(value: str | None) -> bool | None:
    """Convierte un parámetro de query string a booleano opcional."""
    if value is None or value == '':
        return None
    if value.lower() in {'true', '1'}:
        return True
    if value.lower() in {'false', '0'}:
        return False
    return None


def parse_integer(value: str | None) -> int | None:
    """Convierte un identificador positivo válido de query string a entero."""
    return int(value) if value and value.isdigit() else None


def parse_date(value: str | None) -> date | None:
    """Convierte una fecha ISO 8601 (YYYY-MM-DD) de query string a objeto date."""
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
