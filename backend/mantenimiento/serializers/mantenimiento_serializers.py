from rest_framework import serializers

from equipos.models import Equipo
from mantenimiento.models import Mantenimiento
from usuarios.models import Usuario


class EquipoResumenSerializer(serializers.ModelSerializer):
    """Representa los datos minimos del equipo asociado a un ticket."""

    espacio_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Equipo
        fields = ['id', 'codigo', 'marca', 'modelo', 'tipo_equipo', 'espacio_nombre']

    def get_espacio_nombre(self, obj: Equipo) -> str:
        if obj.espacio is None:
            return 'Sin espacio asignado'
        return f'{obj.espacio.codigo_espacio} - {obj.espacio.pabellon}'


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


class MantenimientoResumenSerializer(serializers.ModelSerializer):
    """Representa una orden compacta dentro del detalle de una incidencia."""

    tipo_mantenimiento_display = serializers.CharField(
        source='get_tipo_mantenimiento_display', read_only=True,
    )
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Mantenimiento
        fields = [
            'id',
            'fecha',
            'tipo_mantenimiento',
            'tipo_mantenimiento_display',
            'estado',
            'estado_display',
            'descripcion',
            'diagnostico',
            'trabajo_realizado',
            'resultado_equipo',
            'prueba_realizada',
            'observacion_prueba',
            'fecha_fin',
        ]


class MantenimientoSerializer(serializers.ModelSerializer):
    """Representa un ticket de mantenimiento con sus relaciones expandidas."""

    equipo = EquipoResumenSerializer(read_only=True)
    reportado_por = ReportanteSerializer(read_only=True)
    verificado_por = ReportanteSerializer(read_only=True)
    tipo_mantenimiento_display = serializers.CharField(
        source='get_tipo_mantenimiento_display', read_only=True,
    )
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tecnicos = serializers.SerializerMethodField()
    tecnico_responsable = serializers.SerializerMethodField()
    incidencia_origen_id = serializers.IntegerField(read_only=True, allow_null=True)

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
            'incidencia_origen_id',
            'diagnostico',
            'trabajo_realizado',
            'resultado_equipo',
            'prueba_realizada',
            'observacion_prueba',
            'verificado_por',
            'fecha_verificacion',
            'fecha_inicio',
            'fecha_fin',
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
    incidencia_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    reportado_por_id = serializers.IntegerField(min_value=1, required=False)
    fecha = serializers.DateField()
    tipo_mantenimiento = serializers.ChoiceField(choices=Mantenimiento.TIPO_CHOICES)
    estado = serializers.ChoiceField(choices=Mantenimiento.ESTADO_CHOICES, required=False, default='pendiente')
    descripcion = serializers.CharField(trim_whitespace=True)
    diagnostico = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    trabajo_realizado = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    resultado_equipo = serializers.ChoiceField(
        choices=Mantenimiento.RESULTADO_EQUIPO_CHOICES,
        required=False,
        allow_null=True,
    )
    prueba_realizada = serializers.BooleanField(required=False, default=False)
    observacion_prueba = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    tecnicos_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        default=list,
    )


class MantenimientoFinalizeSerializer(serializers.Serializer):
    """Valida los datos necesarios para cerrar una orden de trabajo."""

    diagnostico = serializers.CharField(trim_whitespace=True)
    trabajo_realizado = serializers.CharField(trim_whitespace=True)
    prueba_realizada = serializers.BooleanField()
    observacion_prueba = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    resultado_equipo = serializers.ChoiceField(
        choices=[
            choice for choice in Mantenimiento.RESULTADO_EQUIPO_CHOICES
            if choice[0] != 'en_mantenimiento'
        ],
    )
