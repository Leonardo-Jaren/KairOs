from rest_framework import serializers

from software.models import ProductoSoftware


class ProductoSoftwareSerializer(serializers.ModelSerializer):
    """Representa un producto de software con sus indicadores de licenciamiento."""

    tipo_licencia_display = serializers.CharField(source='get_tipo_licencia_display', read_only=True)
    licencias_usadas = serializers.IntegerField(read_only=True)
    licencias_disponibles = serializers.IntegerField(read_only=True)
    proxima_a_expirar = serializers.BooleanField(read_only=True)
    sobre_uso = serializers.SerializerMethodField()

    class Meta:
        model = ProductoSoftware
        fields = [
            'id',
            'software',
            'version',
            'descripcion',
            'tipo_licencia',
            'tipo_licencia_display',
            'licencias_totales',
            'licencias_usadas',
            'licencias_disponibles',
            'fecha_expiracion',
            'costo_anual_total',
            'proxima_a_expirar',
            'sobre_uso',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_sobre_uso(self, obj: ProductoSoftware) -> bool:
        """Indica si las instalaciones vigentes superan las licencias totales."""
        return obj.licencias_disponibles < 0


class ProductoSoftwareCreateUpdateSerializer(serializers.ModelSerializer):
    """Valida los datos de creacion y edicion de un producto de software."""

    class Meta:
        model = ProductoSoftware
        fields = [
            'software',
            'version',
            'descripcion',
            'tipo_licencia',
            'licencias_totales',
            'fecha_expiracion',
            'costo_anual_total',
        ]
        extra_kwargs = {
            'software': {'validators': []},
            'version': {'validators': []},
            'fecha_expiracion': {'required': False, 'allow_null': True},
        }
