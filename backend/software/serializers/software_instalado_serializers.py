from rest_framework import serializers

from software.models import SoftwareInstalado


class SoftwareInstaladoSerializer(serializers.ModelSerializer):
    """Representa una instalacion de software con datos del equipo y producto."""

    producto_software_nombre = serializers.SerializerMethodField()
    equipo_codigo = serializers.CharField(source='equipo.codigo', read_only=True)
    espacio_nombre = serializers.SerializerMethodField()

    class Meta:
        model = SoftwareInstalado
        fields = [
            'id',
            'equipo',
            'equipo_codigo',
            'espacio_nombre',
            'producto_software',
            'producto_software_nombre',
            'numero_licencia_usado',
            'fecha_instalacion',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_producto_software_nombre(self, obj: SoftwareInstalado) -> str:
        """Combina nombre y version del producto de software."""
        return f'{obj.producto_software.software} v{obj.producto_software.version}'

    def get_espacio_nombre(self, obj: SoftwareInstalado) -> str | None:
        """Combina codigo y pabellon del espacio del equipo."""
        espacio = obj.equipo.espacio
        if not espacio:
            return None
        return f'{espacio.codigo_espacio} - {espacio.pabellon}'


class SoftwareInstaladoCreateUpdateSerializer(serializers.ModelSerializer):
    """Valida los datos de creacion y edicion de una instalacion de software."""

    class Meta:
        model = SoftwareInstalado
        fields = [
            'equipo',
            'producto_software',
            'numero_licencia_usado',
            'fecha_instalacion',
        ]
        extra_kwargs = {
            'equipo': {'required': False},
            'producto_software': {'required': False},
        }

    def validate(self, attrs):
        """Exige equipo y producto_software solo en creacion (no en edicion parcial)."""
        if self.instance is None:
            if not attrs.get('equipo'):
                raise serializers.ValidationError({'equipo': 'Este campo es requerido.'})
            if not attrs.get('producto_software'):
                raise serializers.ValidationError({'producto_software': 'Este campo es requerido.'})
        return attrs
