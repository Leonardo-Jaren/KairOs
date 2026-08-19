from rest_framework import serializers

from equipos.models import Equipo
from espacios.models import Edificio, Espacio
from espacios.serializers.edificio_serializers import EdificioResumenSerializer
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
    tipo_equipo_display = serializers.CharField(source='get_tipo_equipo_display')
    modo_adquisicion_display = serializers.CharField(source='get_modo_adquisicion_display')
    estado_display = serializers.CharField(source='get_estado_display')

    class Meta:
        model = Equipo
        fields = [
            'id',
            'codigo',
            'numero_serie',
            'numero_mac',
            'tipo_equipo',
            'tipo_display',
            'tipo_equipo_display',
            'marca',
            'modelo',
            'modo_adquisicion',
            'modo_adquisicion_display',
            'fecha_adquisicion',
            'fecha_renovacion',
            'estado',
            'estado_display',
            'responsable_usuario',
        ]


class EspacioSerializer(serializers.ModelSerializer):
    """Representa un espacio con sus indicadores operativos."""

    tipo_display = serializers.CharField(source='get_tipo_display')
    responsable = serializers.SerializerMethodField()
    cantidad_equipos = serializers.SerializerMethodField()
    resumen_equipos = serializers.SerializerMethodField()
    edificio = EdificioResumenSerializer(read_only=True)
    edificio_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Espacio
        fields = [
            'id',
            'codigo_espacio',
            'tipo',
            'tipo_display',
            'pabellon',
            'edificio',
            'edificio_id',
            'piso',
            'activo',
            'responsable',
            'cantidad_equipos',
            'resumen_equipos',
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

    def get_resumen_equipos(self, obj: Espacio) -> dict:
        """Resume el estado operativo de los equipos del espacio."""
        resumen = {
            'en_uso': 0,
            'en_mantenimiento': 0,
            'dañado': 0,
            'de_baja': 0,
        }
        for equipo in getattr(obj, 'equipos_vigentes', []):
            if equipo.estado in resumen:
                resumen[equipo.estado] += 1
        return resumen


class EspacioDetailSerializer(EspacioSerializer):
    """Amplía el espacio con los equipos usados en el diagrama."""

    equipos = serializers.SerializerMethodField()

    class Meta(EspacioSerializer.Meta):
        fields = [*EspacioSerializer.Meta.fields, 'configuracion_plano', 'equipos']

    def get_equipos(self, obj: Espacio):
        return EquipoEspacioSerializer(
            getattr(obj, 'equipos_vigentes', []),
            many=True,
        ).data


class EspacioCreateUpdateSerializer(serializers.ModelSerializer):
    """Valida los datos de creación y edición del espacio."""

    piso = serializers.RegexField(
        regex=r'^\d+$',
        max_length=20,
        error_messages={
            'invalid': 'El piso debe contener únicamente números.',
        },
    )
    edificio_id = serializers.PrimaryKeyRelatedField(
        source='edificio',
        queryset=Edificio.objects.filter(is_deleted=False, activo=True),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Espacio
        fields = [
            'codigo_espacio',
            'tipo',
            'pabellon',
            'edificio_id',
            'piso',
            'activo',
        ]
        extra_kwargs = {
            'codigo_espacio': {'validators': []},
            'pabellon': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        """Acepta edificio o pabellón para mantener clientes anteriores."""
        edificio_actual = self.instance.edificio if self.instance else None
        pabellon_actual = self.instance.pabellon if self.instance else ''
        edificio = attrs.get('edificio', edificio_actual)
        pabellon = attrs.get('pabellon', pabellon_actual).strip()
        if edificio is None and not pabellon:
            raise serializers.ValidationError({
                'pabellon': 'Indique un pabellón o seleccione un edificio.'
            })
        return attrs


class PuestoPlanoSerializer(serializers.Serializer):
    """Valida la ubicación de un equipo dentro de la cuadrícula del espacio."""

    equipo_id = serializers.IntegerField(min_value=1)
    fila = serializers.IntegerField(min_value=1, max_value=20)
    columna = serializers.IntegerField(min_value=1, max_value=10)
    es_docente = serializers.BooleanField(default=False)


class DisposicionEspacioSerializer(serializers.Serializer):
    """Valida la configuración completa de un plano tecnológico."""

    columnas = serializers.IntegerField(min_value=2, max_value=10)
    filas = serializers.IntegerField(min_value=1, max_value=20)
    puestos = PuestoPlanoSerializer(many=True)

    def validate(self, attrs):
        """Impide posiciones repetidas o fuera de las dimensiones declaradas."""
        posiciones = set()
        equipos = set()
        docentes = 0
        for puesto in attrs['puestos']:
            if puesto['fila'] > attrs['filas'] or puesto['columna'] > attrs['columnas']:
                raise serializers.ValidationError(
                    'Todos los puestos deben estar dentro de las filas y columnas del plano.'
                )
            posicion = (puesto['fila'], puesto['columna'])
            if posicion in posiciones:
                raise serializers.ValidationError('Dos equipos no pueden ocupar el mismo puesto.')
            if puesto['equipo_id'] in equipos:
                raise serializers.ValidationError('Un equipo no puede aparecer en más de un puesto.')
            posiciones.add(posicion)
            equipos.add(puesto['equipo_id'])
            docentes += int(puesto.get('es_docente', False))
        if docentes > 1:
            raise serializers.ValidationError(
                'Solo un equipo puede marcarse como estación del docente.'
            )
        return attrs
