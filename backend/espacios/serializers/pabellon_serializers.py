from rest_framework import serializers
from espacios.models import Pabellon


class PabellonReadSerializer(serializers.ModelSerializer):
    """Solo para lectura — respuestas GET."""

    class Meta:
        model  = Pabellon
        fields = ["id_pabellon", "nombre", "descripcion", "total_pisos"]


class PabellonCreateSerializer(serializers.ModelSerializer):
    """Solo para creación — POST /pabellones/"""

    class Meta:
        model  = Pabellon
        fields = ["nombre", "descripcion", "total_pisos"]
        extra_kwargs = {
            "nombre":      {"validators": []},
            "descripcion": {"required": False},
            "total_pisos": {"required": False},
        }


class PabellonUpdateSerializer(serializers.ModelSerializer):
    """Para actualización parcial — PATCH /pabellones/{id}/"""

    class Meta:
        model  = Pabellon
        fields = ["nombre", "descripcion", "total_pisos"]
        extra_kwargs = {
            "nombre":      {"required": False, "validators": []},
            "descripcion": {"required": False},
            "total_pisos": {"required": False},
        }
