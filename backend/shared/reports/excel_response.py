"""Serializa un libro Excel y lo convierte en una respuesta de descarga HTTP."""

import io

from django.http import HttpResponse


class ExcelResponseFactory:
    CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    @staticmethod
    def to_bytes(workbook) -> bytes:
        buffer = io.BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()

    @classmethod
    def to_response(cls, workbook, filename: str) -> HttpResponse:
        if not filename.endswith(".xlsx"):
            filename = f"{filename}.xlsx"

        response = HttpResponse(cls.to_bytes(workbook), content_type=cls.CONTENT_TYPE)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response
