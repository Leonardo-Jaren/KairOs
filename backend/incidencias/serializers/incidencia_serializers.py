from rest_framework import serializers

from incidencias.models import Incidencia


class IncidenciaSerializer(serializers.ModelSerializer):
    """Representa una incidencia con datos de presentacion de sus relaciones."""

    tipo_incidencia_display = serializers.CharField(source='get_tipo_incidencia_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    espacio_nombre = serializers.SerializerMethodField()
    equipo_codigo = serializers.CharField(source='equipo.codigo', read_only=True)
    reportado_por = serializers.SerializerMethodField()
    reportado_por_rol = serializers.CharField(source='created_by.rol', read_only=True, default=None)

    class Meta:
        model = Incidencia
        fields = [
            'id',
            'espacio',
            'espacio_nombre',
            'equipo',
            'equipo_codigo',
            'tipo_incidencia',
            'tipo_incidencia_display',
            'descripcion',
            'estado',
            'estado_display',
            'fecha_resolucion',
            'reportado_por',
            'reportado_por_rol',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_espacio_nombre(self, obj: Incidencia) -> str:
        """Combina codigo y pabellon del espacio afectado."""
        return f'{obj.espacio.codigo_espacio} - {obj.espacio.pabellon}'

    def get_reportado_por(self, obj: Incidencia) -> str | None:
        """Nombre de quien registro la incidencia, sin importar su rol."""
        if not obj.created_by:
            return None
        return f'{obj.created_by.nombre} {obj.created_by.apellido}'.strip()


class IncidenciaCreateUpdateSerializer(serializers.ModelSerializer):
    """Valida los datos de creacion y edicion de una incidencia."""

    class Meta:
        model = Incidencia
        fields = [
            'espacio',
            'equipo',
            'tipo_incidencia',
            'descripcion',
            'estado',
        ]
        extra_kwargs = {
            'espacio': {'required': False},
            'equipo': {'required': False},
            'tipo_incidencia': {'required': False},
            'descripcion': {'required': False},
            'estado': {'required': False},
        }

    def validate(self, attrs):
        """Exige los campos de reporte solo en creacion, no en edicion parcial."""
        if self.instance is None:
            requeridos = ['espacio', 'equipo', 'tipo_incidencia', 'descripcion']
            faltantes = {campo: 'Este campo es requerido.' for campo in requeridos if not attrs.get(campo)}
            if faltantes:
                raise serializers.ValidationError(faltantes)
        return attrs
