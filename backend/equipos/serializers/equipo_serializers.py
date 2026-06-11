from rest_framework import serializers
from equipos.models import Equipo, Componente
from espacios.models import Espacio
from usuarios.models import Usuario


class ComponenteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Componente
        fields = ["id_componente", "tipo", "modelo", "numero_serie", "descripcion"]


class ResponsableSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Usuario
        fields = ["id_usuario", "nombre", "correo"]


class EspacioResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Espacio
        fields = ["id_espacio", "codigo_espacio", "tipo"]


class EquipoReadSerializer(serializers.ModelSerializer):
    """Lectura completa — incluye espacio, responsable y componentes anidados."""
    espacio     = EspacioResumenSerializer(read_only=True, default=None)
    responsable = ResponsableSerializer(read_only=True, default=None)
    componentes = ComponenteSerializer(many=True, read_only=True)

    class Meta:
        model  = Equipo
        fields = [
            "id_equipo", "codigo", "tipo_equipo", "marca", "modelo",
            "numero_serie", "numero_mac", "modo_adquisicion",
            "fecha_adquisicion", "fecha_renovacion", "estado",
            "espacio", "responsable", "componentes",
        ]


class EquipoCreateSerializer(serializers.ModelSerializer):
    """Creación — POST /equipos/"""
    espacio = serializers.PrimaryKeyRelatedField(
        queryset=Espacio.objects.all(), required=False, allow_null=True
    )
    responsable = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model  = Equipo
        fields = [
            "codigo", "tipo_equipo", "marca", "modelo",
            "numero_serie", "numero_mac", "modo_adquisicion",
            "fecha_adquisicion", "fecha_renovacion", "estado",
            "espacio", "responsable",
        ]
        extra_kwargs = {
            "codigo":             {"validators": []},
            "tipo_equipo":        {"required": False},
            "marca":              {"required": False},
            "modelo":             {"required": False},
            "numero_serie":       {"required": False},
            "numero_mac":         {"required": False},
            "modo_adquisicion":   {"required": False},
            "fecha_adquisicion":  {"required": False},
            "fecha_renovacion":   {"required": False},
            "estado":             {"required": False},
        }


class EquipoUpdateSerializer(serializers.ModelSerializer):
    """Actualización parcial — PATCH /equipos/{id}/"""
    espacio = serializers.PrimaryKeyRelatedField(
        queryset=Espacio.objects.all(), required=False, allow_null=True
    )
    responsable = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model  = Equipo
        fields = [
            "codigo", "tipo_equipo", "marca", "modelo",
            "numero_serie", "numero_mac", "modo_adquisicion",
            "fecha_adquisicion", "fecha_renovacion", "estado",
            "espacio", "responsable",
        ]
        extra_kwargs = {field: {"required": False} for field in [
            "codigo", "tipo_equipo", "marca", "modelo", "numero_serie",
            "numero_mac", "modo_adquisicion", "fecha_adquisicion",
            "fecha_renovacion", "estado",
        ]}
        extra_kwargs["codigo"] = {"required": False, "validators": []}
