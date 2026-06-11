from rest_framework import serializers
from software.models import SoftwareInstalado, ProductoSoftware
from equipos.models import Equipo


class ProductoResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductoSoftware
        fields = ["id_producto_software", "software", "version", "tipo_licencia"]


class EquipoResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Equipo
        fields = ["id_equipo", "codigo", "marca", "modelo"]


class InstalacionReadSerializer(serializers.ModelSerializer):
    """Lectura — muestra equipo y producto anidados."""
    equipo            = EquipoResumenSerializer(read_only=True)
    producto_software = ProductoResumenSerializer(read_only=True)

    class Meta:
        model  = SoftwareInstalado
        fields = [
            "id_instalacion", "equipo", "producto_software",
            "numero_licencia_usado", "fecha_instalacion",
        ]


class InstalacionCreateSerializer(serializers.ModelSerializer):
    """
    Creación — recibe PKs.
    La validación de licencias disponibles la hace el service,
    no el serializer (SRP).
    """
    equipo            = serializers.PrimaryKeyRelatedField(queryset=Equipo.objects.all())
    producto_software = serializers.PrimaryKeyRelatedField(queryset=ProductoSoftware.objects.all())

    class Meta:
        model  = SoftwareInstalado
        fields = ["equipo", "producto_software", "numero_licencia_usado", "fecha_instalacion"]
        extra_kwargs = {
            "numero_licencia_usado": {"required": False},
            "fecha_instalacion":     {"required": False},
        }
