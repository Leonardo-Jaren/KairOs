from rest_framework import serializers
from equipos.models import Componente, Equipo


class ComponenteReadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Componente
        fields = ["id_componente", "equipo", "tipo", "modelo", "numero_serie", "descripcion"]


class ComponenteCreateSerializer(serializers.ModelSerializer):
    equipo = serializers.PrimaryKeyRelatedField(queryset=Equipo.objects.all())

    class Meta:
        model  = Componente
        fields = ["equipo", "tipo", "modelo", "numero_serie", "descripcion"]
        extra_kwargs = {
            "tipo":         {"required": False},
            "modelo":       {"required": False},
            "numero_serie": {"required": False},
            "descripcion":  {"required": False},
        }


class ComponenteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Componente
        fields = ["tipo", "modelo", "numero_serie", "descripcion"]
        extra_kwargs = {field: {"required": False} for field in fields}
