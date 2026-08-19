from rest_framework import serializers

from software.models import ProductoSoftware


class ProductoSoftwareResumenSerializer(serializers.ModelSerializer):
    """Representa los datos necesarios para identificar un producto."""

    tipo_licencia_display = serializers.CharField(
        source='get_tipo_licencia_display',
        read_only=True,
    )

    class Meta:
        model = ProductoSoftware
        fields = [
            'id',
            'software',
            'version',
            'tipo_licencia',
            'tipo_licencia_display',
            'fecha_expiracion',
        ]
        read_only_fields = fields


class ProductoSoftwareSerializer(ProductoSoftwareResumenSerializer):
    """Representa el catalogo junto con la disponibilidad de licencias."""

    licencias_usadas = serializers.IntegerField(read_only=True)
    licencias_disponibles = serializers.SerializerMethodField()

    class Meta(ProductoSoftwareResumenSerializer.Meta):
        fields = ProductoSoftwareResumenSerializer.Meta.fields + [
            'descripcion',
            'licencias_totales',
            'licencias_usadas',
            'licencias_disponibles',
            'costo_anual_total',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_licencias_disponibles(
        self,
        obj: ProductoSoftware,
    ) -> int | None:
        """Calcula disponibilidad sin contar instalaciones retiradas."""
        if obj.tipo_licencia == 'libre':
            return None
        return max(obj.licencias_totales - obj.licencias_usadas, 0)
