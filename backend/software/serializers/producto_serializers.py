from rest_framework import serializers
from software.models import ProductoSoftware


class ProductoSoftwareReadSerializer(serializers.ModelSerializer):
    """Lectura — incluye campos calculados de licencias."""
    licencias_usadas      = serializers.IntegerField(read_only=True)
    licencias_disponibles = serializers.IntegerField(read_only=True)
    licencia_vencida      = serializers.BooleanField(read_only=True)

    class Meta:
        model  = ProductoSoftware
        fields = [
            "id_producto_software", "software", "version", "descripcion",
            "tipo_licencia", "licencias_totales", "licencias_usadas",
            "licencias_disponibles", "fecha_expiracion", "licencia_vencida",
            "costo_anual_total",
        ]


class ProductoSoftwareCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductoSoftware
        fields = [
            "software", "version", "descripcion", "tipo_licencia",
            "licencias_totales", "fecha_expiracion", "costo_anual_total",
        ]
        extra_kwargs = {
            "software":         {"validators": []},
            "version":          {"required": False},
            "descripcion":      {"required": False},
            "tipo_licencia":    {"required": False},
            "licencias_totales":{"required": False},
            "fecha_expiracion": {"required": False},
            "costo_anual_total":{"required": False},
        }


class ProductoSoftwareUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductoSoftware
        fields = [
            "software", "version", "descripcion", "tipo_licencia",
            "licencias_totales", "fecha_expiracion", "costo_anual_total",
        ]
        extra_kwargs = {field: {"required": False} for field in fields}
        extra_kwargs["software"] = {"required": False, "validators": []}
