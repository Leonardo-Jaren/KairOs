from rest_framework import serializers

from equipos.models import Equipo
from espacios.models import Espacio
from usuarios.models import Usuario


class ResponsableEspacioSerializer(serializers.ModelSerializer):
    """Representa al responsable principal de un espacio."""

    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'nombre_completo', 'correo']

    def get_nombre_completo(self, obj: Usuario) -> str:
        return f'{obj.nombre} {obj.apellido}'.strip()


class EquipoEspacioSerializer(serializers.ModelSerializer):
    """Representa un equipo dentro del diagrama del espacio."""

    tipo_display = serializers.CharField(source='get_tipo_equipo_display')
    estado_display = serializers.CharField(source='get_estado_display')

    class Meta:
        model = Equipo
        fields = [
            'id',
            'codigo',
            'tipo_equipo',
            'tipo_display',
            'marca',
            'modelo',
            'estado',
            'estado_display',
        ]


class EspacioSerializer(serializers.ModelSerializer):
    """Representa un espacio con sus indicadores operativos."""

    tipo_display = serializers.CharField(source='get_tipo_display')
    responsable = serializers.SerializerMethodField()
    cantidad_equipos = serializers.SerializerMethodField()

    class Meta:
        model = Espacio
        fields = [
            'id',
            'codigo_espacio',
            'tipo',
            'tipo_display',
            'pabellon',
            'piso',
            'activo',
            'responsable',
            'cantidad_equipos',
            'created_at',
            'updated_at',
        ]

    def get_responsable(self, obj: Espacio):
        asignaciones = getattr(obj, 'asignaciones_activas', [])
        asignacion = next(
            (
                item for item in asignaciones
                if item.tipo_responsabilidad == 'responsable'
            ),
            asignaciones[0] if asignaciones else None,
        )
        if asignacion is None:
            return None
        return ResponsableEspacioSerializer(asignacion.usuario).data

    def get_cantidad_equipos(self, obj: Espacio) -> int:
        return len(getattr(obj, 'equipos_vigentes', []))


class EspacioDetailSerializer(EspacioSerializer):
    """Amplía el espacio con los equipos usados en el diagrama."""

    equipos = serializers.SerializerMethodField()

    class Meta(EspacioSerializer.Meta):
        fields = [*EspacioSerializer.Meta.fields, 'equipos']

    def get_equipos(self, obj: Espacio):
        return EquipoEspacioSerializer(
            getattr(obj, 'equipos_vigentes', []),
            many=True,
        ).data


class EspacioCreateUpdateSerializer(serializers.ModelSerializer):
    """Valida los datos de creación y edición del espacio."""

    class Meta:
        model = Espacio
        fields = ['codigo_espacio', 'tipo', 'pabellon', 'piso', 'activo']
        extra_kwargs = {
            'codigo_espacio': {'validators': []},
        }
