from rest_framework import serializers

from equipos.models import Equipo
from mantenimiento.models import Mantenimiento
from usuarios.models import Usuario


class EquipoResumenSerializer(serializers.ModelSerializer):
    """Representa los datos minimos del equipo asociado a un ticket."""

    class Meta:
        model = Equipo
        fields = ['id', 'codigo', 'marca', 'modelo', 'tipo_equipo']


class ReportanteSerializer(serializers.ModelSerializer):
    """Representa los datos mínimos del usuario que reportó el ticket."""

    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'nombre_completo', 'correo', 'rol']

    def get_nombre_completo(self, obj: Usuario) -> str:
        """Combina nombre y apellido del usuario reportante."""
        return f'{obj.nombre} {obj.apellido}'.strip()


class TecnicoAsignadoSerializer(serializers.Serializer):
    """Representa un tecnico asignado dentro de un ticket de mantenimiento."""

    id = serializers.IntegerField(source='tecnico.id')
    nombre_completo = serializers.SerializerMethodField()
    area = serializers.CharField(source='tecnico.area')

    def get_nombre_completo(self, obj) -> str:
        """Combina nombre y apellido del usuario tecnico."""
        usuario = obj.tecnico.usuario
        return f'{usuario.nombre} {usuario.apellido}'.strip()


class MantenimientoSerializer(serializers.ModelSerializer):
    """Representa un ticket de mantenimiento con sus relaciones expandidas."""

    equipo = EquipoResumenSerializer(read_only=True)
    reportado_por = ReportanteSerializer(read_only=True)
    tipo_mantenimiento_display = serializers.CharField(
        source='get_tipo_mantenimiento_display', read_only=True,
    )
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tecnicos = serializers.SerializerMethodField()
    tecnico_responsable = serializers.SerializerMethodField()

    class Meta:
        model = Mantenimiento
        fields = [
            'id',
            'equipo',
            'reportado_por',
            'fecha',
            'tipo_mantenimiento',
            'tipo_mantenimiento_display',
            'estado',
            'estado_display',
            'descripcion',
            'tecnicos',
            'tecnico_responsable',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_tecnicos(self, obj: Mantenimiento):
        """Lista los tecnicos asignados al ticket."""
        asignaciones = obj.tecnicos_asignados.all()
        return TecnicoAsignadoSerializer(asignaciones, many=True).data

    def get_tecnico_responsable(self, obj: Mantenimiento) -> str:
        """Muestra el primer tecnico asignado como responsable principal."""
        asignacion = obj.tecnicos_asignados.all()[:1]
        if not asignacion:
            return 'Sin asignar'
        usuario = asignacion[0].tecnico.usuario
        return f'{usuario.nombre} {usuario.apellido}'.strip()


class MantenimientoCreateUpdateSerializer(serializers.Serializer):
    """Valida el formato de los datos de creacion y edicion de un ticket."""

    equipo_id = serializers.IntegerField(min_value=1)
    reportado_por_id = serializers.IntegerField(min_value=1, required=False)
    fecha = serializers.DateField()
    tipo_mantenimiento = serializers.ChoiceField(choices=Mantenimiento.TIPO_CHOICES)
    estado = serializers.ChoiceField(choices=Mantenimiento.ESTADO_CHOICES, required=False, default='pendiente')
    descripcion = serializers.CharField(trim_whitespace=True)
    tecnicos_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        default=list,
    )
