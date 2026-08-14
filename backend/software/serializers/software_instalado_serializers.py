from rest_framework import serializers

from software.models import SoftwareInstalado
from software.serializers.producto_software_serializers import (
    ProductoSoftwareResumenSerializer,
)


class SoftwareInstaladoSerializer(serializers.ModelSerializer):
    """Representa una instalacion con el equipo y producto asociados."""

    equipo_codigo = serializers.CharField(source='equipo.codigo', read_only=True)
    producto = ProductoSoftwareResumenSerializer(
        source='producto_software',
        read_only=True,
    )

    class Meta:
        model = SoftwareInstalado
        fields = [
            'id',
            'equipo',
            'equipo_codigo',
            'producto_software',
            'producto',
            'numero_licencia_usado',
            'fecha_instalacion',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class SoftwareInstaladoCreateSerializer(serializers.ModelSerializer):
    """Valida los datos necesarios para instalar software en un equipo."""

    equipo_id = serializers.IntegerField(write_only=True)
    producto_software_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = SoftwareInstalado
        fields = [
            'equipo_id',
            'producto_software_id',
            'numero_licencia_usado',
            'fecha_instalacion',
        ]
        extra_kwargs = {
            'numero_licencia_usado': {
                'required': False,
                'allow_blank': True,
            },
        }
