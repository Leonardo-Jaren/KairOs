from django.db.models import Q
from rest_framework import serializers

from equipos.models import Equipo
from espacios.models import Edificio, Espacio, EspacioUsuario
from espacios.serializers.edificio_serializers import EdificioResumenSerializer
from espacios.serializers.espacio_usuario_serializers import UsuarioResumenSerializer
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


class EncargadoTerritorialSerializer(serializers.ModelSerializer):
    """Representa un encargado asignado a un ámbito territorial (directo o heredado)."""

    usuario = UsuarioResumenSerializer(read_only=True)
    usuario_id = serializers.IntegerField(source='usuario.id', read_only=True)
    usuario_nombre = serializers.SerializerMethodField()
    usuario_email = serializers.CharField(source='usuario.correo', read_only=True)
    tipo_responsabilidad_display = serializers.CharField(
        source='get_tipo_responsabilidad_display',
        read_only=True,
    )
    ambito_display = serializers.CharField(
        source='get_ambito_display',
        read_only=True,
    )
    origen = serializers.SerializerMethodField()

    class Meta:
        model = EspacioUsuario
        fields = [
            'id',
            'usuario',
            'usuario_id',
            'usuario_nombre',
            'usuario_email',
            'tipo_responsabilidad',
            'tipo_responsabilidad_display',
            'ambito',
            'ambito_display',
            'origen',
            'badge_texto',
            'activo',
        ]

    def get_usuario_nombre(self, obj: EspacioUsuario) -> str:
        if not obj.usuario:
            return ''
        return f'{obj.usuario.nombre} {obj.usuario.apellido}'.strip()

    def get_origen(self, obj: EspacioUsuario) -> str:
        """Determina la procedencia territorial del encargado."""
        if obj.ambito == EspacioUsuario.AMBITO_PISO:
            edif_nombre = obj.edificio.nombre if obj.edificio else 'Pabellón'
            return f'Piso {obj.piso} · {edif_nombre}' if obj.piso else edif_nombre
        if obj.ambito == EspacioUsuario.AMBITO_EDIFICIO:
            return obj.edificio.nombre if obj.edificio else 'Edificio'
        if obj.ambito == EspacioUsuario.AMBITO_SEDE:
            return obj.local.nombre if obj.local else 'Sede Central'
        if obj.espacio:
            return obj.espacio.codigo_espacio
        return ''


class EspacioSerializer(serializers.ModelSerializer):
    """Representa un espacio con sus indicadores operativos y cadena de mandos territoriales."""

    tipo_display = serializers.CharField(source='get_tipo_display')
    responsable = serializers.SerializerMethodField()
    encargados_directos = serializers.SerializerMethodField()
    encargados_heredados = serializers.SerializerMethodField()
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
            'encargados_directos',
            'encargados_heredados',
            'cantidad_equipos',
            'resumen_equipos',
            'created_at',
            'updated_at',
        ]

    def _get_asignaciones_directas(self, obj: Espacio) -> list[EspacioUsuario]:
        """Obtiene las asignaciones vinculadas directamente al espacio físico."""
        directas = getattr(obj, 'asignaciones_activas', None)
        if directas is None:
            directas = list(
                obj.asignaciones_usuario.filter(
                    is_deleted=False,
                    activo=True,
                ).select_related('usuario', 'espacio')
            )
        return [
            a for a in directas
            if a.activo and not a.is_deleted and (a.ambito == EspacioUsuario.AMBITO_ESPACIO or a.espacio_id == obj.id)
        ]

    def _get_asignaciones_heredadas(self, obj: Espacio) -> list[EspacioUsuario]:
        """
        Retorna las asignaciones de niveles superiores que cubren este espacio:
        1. Piso: donde edificio_id == obj.edificio_id y piso == obj.piso
        2. Edificio: donde edificio_id == obj.edificio_id
        3. Sede: donde local_id == obj.edificio.local_id
        """
        edificio = getattr(obj, 'edificio', None)
        if not edificio:
            return []

        # Caso Optimizado: Si ya se precargaron en el Repositorio
        if hasattr(edificio, 'asignaciones_edificio_activas'):
            asignaciones_edificio = getattr(edificio, 'asignaciones_edificio_activas', [])
            piso_str = str(obj.piso).strip() if obj.piso else ''

            asig_piso = [
                a for a in asignaciones_edificio
                if a.activo and not a.is_deleted
                and a.ambito == EspacioUsuario.AMBITO_PISO
                and str(a.piso).strip() == piso_str
            ]
            asig_edificio = [
                a for a in asignaciones_edificio
                if a.activo and not a.is_deleted
                and a.ambito == EspacioUsuario.AMBITO_EDIFICIO
            ]

            local = getattr(edificio, 'local', None)
            asig_sede = []
            if local and hasattr(local, 'asignaciones_sede_activas'):
                asig_sede = [
                    a for a in getattr(local, 'asignaciones_sede_activas', [])
                    if a.activo and not a.is_deleted
                    and a.ambito == EspacioUsuario.AMBITO_SEDE
                ]
            elif local:
                asig_sede = list(
                    EspacioUsuario.objects.filter(
                        is_deleted=False,
                        activo=True,
                        ambito=EspacioUsuario.AMBITO_SEDE,
                        local_id=local.id,
                    ).select_related('usuario', 'local')
                )

            return asig_piso + asig_edificio + asig_sede

        # Caso Fallback: consulta directa optimizada en una sola query
        piso_str = str(obj.piso).strip() if obj.piso else ''
        condiciones = Q(
            ambito=EspacioUsuario.AMBITO_EDIFICIO,
            edificio_id=edificio.id,
        )
        if piso_str:
            condiciones |= Q(
                ambito=EspacioUsuario.AMBITO_PISO,
                edificio_id=edificio.id,
                piso=piso_str,
            )
        local_id = edificio.local_id
        if local_id:
            condiciones |= Q(
                ambito=EspacioUsuario.AMBITO_SEDE,
                local_id=local_id,
            )

        heredadas = list(
            EspacioUsuario.objects.filter(
                condiciones,
                is_deleted=False,
                activo=True,
            ).select_related('usuario', 'edificio', 'local')
        )

        orden_ambito = {
            EspacioUsuario.AMBITO_PISO: 1,
            EspacioUsuario.AMBITO_EDIFICIO: 2,
            EspacioUsuario.AMBITO_SEDE: 3,
        }
        heredadas.sort(key=lambda a: (orden_ambito.get(a.ambito, 99), a.tipo_responsabilidad))
        return heredadas

    def get_encargados_directos(self, obj: Espacio):
        directas = self._get_asignaciones_directas(obj)
        return EncargadoTerritorialSerializer(directas, many=True).data

    def get_encargados_heredados(self, obj: Espacio):
        heredadas = self._get_asignaciones_heredadas(obj)
        return EncargadoTerritorialSerializer(heredadas, many=True).data

    def get_responsable(self, obj: Espacio):
        """
        Resuelve al responsable del espacio:
        1. Encargado directo (preferencia rol 'responsable', o primer directo).
        2. Fallback a encargado heredado operativo más específico (Piso -> Edificio -> Sede).
        """
        directas = self._get_asignaciones_directas(obj)
        if directas:
            asignacion = next(
                (item for item in directas if item.tipo_responsabilidad == 'responsable'),
                directas[0],
            )
            if asignacion and asignacion.usuario:
                return ResponsableEspacioSerializer(asignacion.usuario).data

        heredadas = self._get_asignaciones_heredadas(obj)
        for ambito_objetivo in [EspacioUsuario.AMBITO_PISO, EspacioUsuario.AMBITO_EDIFICIO, EspacioUsuario.AMBITO_SEDE]:
            candidatos = [a for a in heredadas if a.ambito == ambito_objetivo]
            if candidatos:
                asignacion = next(
                    (item for item in candidatos if item.tipo_responsabilidad == 'responsable'),
                    candidatos[0],
                )
                if asignacion and asignacion.usuario:
                    return ResponsableEspacioSerializer(asignacion.usuario).data

        return None

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
