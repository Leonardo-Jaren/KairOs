from rest_framework import serializers
from espacios.models import Espacio, Pabellon
from espacios.serializers.pabellon_serializers import PabellonReadSerializer


class EspacioReadSerializer(serializers.ModelSerializer):
    """Solo para lectura — incluye pabellón anidado."""
    pabellon = PabellonReadSerializer(read_only=True, default=None)

    class Meta:
        model  = Espacio
        fields = [
            "id_espacio", "codigo_espacio", "pabellon",
            "piso", "tipo", "capacidad", "descripcion",
        ]


class EspacioCreateSerializer(serializers.ModelSerializer):
    """Solo para creación — POST /espacios/"""
    pabellon = serializers.PrimaryKeyRelatedField(
        queryset=Pabellon.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model  = Espacio
        fields = ["codigo_espacio", "pabellon", "piso", "tipo", "capacidad", "descripcion"]
        extra_kwargs = {
            "codigo_espacio": {"validators": []},
            "piso":           {"required": False},
            "tipo":           {"required": False},
            "capacidad":      {"required": False},
            "descripcion":    {"required": False},
        }


class EspacioUpdateSerializer(serializers.ModelSerializer):
    """Para actualización parcial — PATCH /espacios/{id}/"""
    pabellon = serializers.PrimaryKeyRelatedField(
        queryset=Pabellon.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model  = Espacio
        fields = ["codigo_espacio", "pabellon", "piso", "tipo", "capacidad", "descripcion"]
        extra_kwargs = {
            "codigo_espacio": {"required": False, "validators": []},
            "piso":           {"required": False},
            "tipo":           {"required": False},
            "capacidad":      {"required": False},
            "descripcion":    {"required": False},
        }
