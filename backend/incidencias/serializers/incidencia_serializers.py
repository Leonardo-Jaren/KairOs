from rest_framework import serializers

from incidencias.models import Incidencia
from usuarios.models import PerfilTecnico


class TecnicoAsignadoSerializer(serializers.ModelSerializer):
    """Representa el tecnico asignado a una incidencia."""

    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = PerfilTecnico
        fields = ['id', 'nombre_completo', 'area', 'usuario_id']

    def get_nombre_completo(self, obj: PerfilTecnico) -> str:
        return f'{obj.usuario.nombre} {obj.usuario.apellido}'.strip()


class IncidenciaSerializer(serializers.ModelSerializer):
    """Representa una incidencia con contexto operativo y trazabilidad."""

    tipo_incidencia_display = serializers.CharField(source='get_tipo_incidencia_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    espacio_nombre = serializers.SerializerMethodField()
    equipo_codigo = serializers.CharField(source='equipo.codigo', read_only=True)
    reportado_por = serializers.SerializerMethodField()
    reportado_por_rol = serializers.CharField(source='created_by.rol', read_only=True, default=None)
    tecnico_asignado = TecnicoAsignadoSerializer(source='asignado_a', read_only=True)
    mantenimientos_count = serializers.SerializerMethodField()
    mantenimientos = serializers.SerializerMethodField()
    requiere_otra_intervencion = serializers.SerializerMethodField()

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
            'prioridad',
            'prioridad_display',
            'estado',
            'estado_display',
            'resolucion',
            'motivo_cierre',
            'fecha_resolucion',
            'tecnico_asignado',
            'mantenimientos_count',
            'mantenimientos',
            'requiere_otra_intervencion',
            'reportado_por',
            'reportado_por_rol',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_espacio_nombre(self, obj: Incidencia) -> str:
        return f'{obj.espacio.codigo_espacio} - {obj.espacio.pabellon}'

    def get_reportado_por(self, obj: Incidencia) -> str | None:
        if not obj.created_by:
            return None
        return f'{obj.created_by.nombre} {obj.created_by.apellido}'.strip()

    def get_mantenimientos_count(self, obj: Incidencia) -> int:
        return sum(1 for ticket in obj.mantenimientos.all() if not ticket.is_deleted)

    def get_mantenimientos(self, obj: Incidencia):
        from mantenimiento.serializers import MantenimientoResumenSerializer

        tickets = [ticket for ticket in obj.mantenimientos.all() if not ticket.is_deleted]
        return MantenimientoResumenSerializer(tickets, many=True).data

    def get_requiere_otra_intervencion(self, obj: Incidencia) -> bool:
        """Indica si una orden terminada dejó el equipo sin recuperar."""
        if obj.estado in {'cerrado', 'cancelado', 'duplicado'}:
            return False
        return any(
            ticket.estado == 'resuelto'
            and ticket.resultado_equipo in {'dañado', 'de_baja'}
            for ticket in obj.mantenimientos.all()
            if not ticket.is_deleted
        )


class IncidenciaCreateSerializer(serializers.ModelSerializer):
    """Valida un reporte inicial; toda incidencia nace pendiente."""

    class Meta:
        model = Incidencia
        fields = ['espacio', 'equipo', 'tipo_incidencia', 'descripcion', 'prioridad']
        extra_kwargs = {
            'descripcion': {'trim_whitespace': True},
            'prioridad': {'required': False, 'default': 'media'},
        }

    def validate(self, attrs):
        if not attrs.get('espacio') or not attrs.get('equipo'):
            raise serializers.ValidationError('El espacio y el equipo son obligatorios.')
        if not attrs.get('descripcion', '').strip():
            raise serializers.ValidationError({'descripcion': 'Describe la falla observada.'})
        return attrs


class IncidenciaUpdateSerializer(serializers.ModelSerializer):
    """Valida los cambios operativos realizados por soporte técnico."""

    asignado_a = serializers.PrimaryKeyRelatedField(
        queryset=PerfilTecnico.objects.filter(is_deleted=False, usuario__is_active=True),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Incidencia
        fields = [
            'espacio',
            'equipo',
            'tipo_incidencia',
            'descripcion',
            'prioridad',
            'estado',
            'asignado_a',
            'resolucion',
            'motivo_cierre',
        ]
        extra_kwargs = {
            'espacio': {'required': False},
            'equipo': {'required': False},
            'tipo_incidencia': {'required': False},
            'descripcion': {'required': False, 'trim_whitespace': True},
            'prioridad': {'required': False},
            'estado': {'required': False},
            'resolucion': {'required': False, 'allow_blank': True, 'trim_whitespace': True},
            'motivo_cierre': {'required': False, 'allow_blank': True, 'trim_whitespace': True},
        }


# Compatibilidad para consumidores que todavía importen el serializer anterior.
IncidenciaCreateUpdateSerializer = IncidenciaUpdateSerializer
