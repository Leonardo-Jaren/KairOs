from rest_framework import serializers

from espacios.models import Edificio, Espacio, EspacioUsuario, Local
from espacios.serializers.edificio_serializers import EdificioResumenSerializer
from espacios.serializers.local_serializers import LocalResumenSerializer
from usuarios.models import Usuario


class UsuarioResumenSerializer(serializers.ModelSerializer):
    """Representa los datos mínimos del usuario asignado."""

    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'nombre_completo', 'correo', 'rol']

    def get_nombre_completo(self, obj: Usuario) -> str:
        """Combina nombres y apellidos para presentación."""
        return f'{obj.nombre} {obj.apellido}'.strip()


class EspacioResumenSerializer(serializers.ModelSerializer):
    """Representa los datos mínimos del espacio asignado."""

    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Espacio
        fields = [
            'id',
            'codigo_espacio',
            'tipo',
            'tipo_display',
            'pabellon',
            'piso',
        ]


class EspacioUsuarioSerializer(serializers.ModelSerializer):
    """Representa una asignación con sus relaciones expandidas y metadatos de ámbito."""

    usuario = UsuarioResumenSerializer(read_only=True)
    local = LocalResumenSerializer(read_only=True)
    edificio = EdificioResumenSerializer(read_only=True)
    espacio = EspacioResumenSerializer(read_only=True)

    ambito_display = serializers.CharField(
        source='get_ambito_display',
        read_only=True,
    )
    tipo_responsabilidad_display = serializers.CharField(
        source='get_tipo_responsabilidad_display',
        read_only=True,
    )

    local_id = serializers.IntegerField(source='local.id', read_only=True, default=None)
    local_nombre = serializers.SerializerMethodField()
    edificio_id = serializers.IntegerField(source='edificio.id', read_only=True, default=None)
    edificio_nombre = serializers.SerializerMethodField()
    espacio_id = serializers.IntegerField(source='espacio.id', read_only=True, default=None)
    espacio_codigo = serializers.SerializerMethodField()
    ubicacion_display = serializers.SerializerMethodField()

    class Meta:
        model = EspacioUsuario
        fields = [
            'id',
            'ambito',
            'ambito_display',
            'usuario',
            'local_id',
            'local_nombre',
            'local',
            'edificio_id',
            'edificio_nombre',
            'edificio',
            'piso',
            'espacio_id',
            'espacio_codigo',
            'espacio',
            'ubicacion_display',
            'tipo_responsabilidad',
            'tipo_responsabilidad_display',
            'activo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_local_nombre(self, obj: EspacioUsuario) -> str | None:
        return obj.local.nombre if obj.local else None

    def get_edificio_nombre(self, obj: EspacioUsuario) -> str | None:
        return obj.edificio.nombre if obj.edificio else None

    def get_espacio_codigo(self, obj: EspacioUsuario) -> str | None:
        return obj.espacio.codigo_espacio if obj.espacio else None

    def get_ubicacion_display(self, obj: EspacioUsuario) -> str:
        """Formatea el nombre del área asignada según el nivel territorial."""
        if obj.ambito == EspacioUsuario.AMBITO_SEDE:
            return obj.local.nombre if obj.local else 'Sede institucional'
        if obj.ambito == EspacioUsuario.AMBITO_EDIFICIO:
            return obj.edificio.nombre if obj.edificio else 'Pabellón / Edificio'
        if obj.ambito == EspacioUsuario.AMBITO_PISO:
            edif_nombre = obj.edificio.nombre if obj.edificio else 'Pabellón'
            return f'{edif_nombre} · Piso {obj.piso}' if obj.piso else edif_nombre
        if obj.ambito == EspacioUsuario.AMBITO_ESPACIO:
            if not obj.espacio:
                return 'Espacio individual'
            edif_nombre = obj.edificio.nombre if obj.edificio else (obj.espacio.pabellon or '')
            if edif_nombre:
                return f'{obj.espacio.codigo_espacio} · {edif_nombre}'
            return obj.espacio.codigo_espacio
        return ''


class EspacioUsuarioCreateUpdateSerializer(serializers.Serializer):
    """Valida el formato y la integridad de una asignación territorial por ámbito."""

    ambito = serializers.ChoiceField(
        choices=EspacioUsuario.AMBITO_CHOICES,
        required=False,
        default=EspacioUsuario.AMBITO_ESPACIO,
    )
    usuario_id = serializers.IntegerField(min_value=1, required=False)
    local_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    edificio_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    piso = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    espacio_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    tipo_responsabilidad = serializers.ChoiceField(
        choices=EspacioUsuario.TIPO_RESPONSABILIDAD_CHOICES,
        required=False,
        default='responsable',
    )
    activo = serializers.BooleanField(required=False, default=True)

    def validate(self, attrs):
        """Valida que los campos obligatorios para el nivel territorial seleccionado estén presentes."""
        errors = {}

        # Determinar ámbito (soporte legacy por defecto a espacio si se omite)
        ambito = attrs.get('ambito')
        if not ambito:
            if self.instance is not None:
                ambito = self.instance.ambito
            else:
                ambito = EspacioUsuario.AMBITO_ESPACIO
            attrs['ambito'] = ambito

        # Al crear, usuario_id es siempre requerido
        if self.instance is None and 'usuario_id' not in attrs:
            errors['usuario_id'] = 'Este campo es obligatorio.'

        # Validaciones específicas por nivel territorial
        if ambito == EspacioUsuario.AMBITO_SEDE:
            local_id = attrs.get('local_id') if 'local_id' in attrs else (
                self.instance.local_id if self.instance else None
            )
            if not local_id:
                errors['local_id'] = 'Este campo es obligatorio para el ámbito de sede.'

        elif ambito == EspacioUsuario.AMBITO_EDIFICIO:
            edificio_id = attrs.get('edificio_id') if 'edificio_id' in attrs else (
                self.instance.edificio_id if self.instance else None
            )
            if not edificio_id:
                errors['edificio_id'] = 'Este campo es obligatorio para el ámbito de edificio.'

        elif ambito == EspacioUsuario.AMBITO_PISO:
            edificio_id = attrs.get('edificio_id') if 'edificio_id' in attrs else (
                self.instance.edificio_id if self.instance else None
            )
            if not edificio_id:
                errors['edificio_id'] = 'Este campo es obligatorio para el ámbito de piso.'

            piso = attrs.get('piso') if 'piso' in attrs else (
                self.instance.piso if self.instance else None
            )
            if piso is None or str(piso).strip() == '':
                errors['piso'] = 'Este campo es obligatorio para el ámbito de piso.'
            else:
                attrs['piso'] = str(piso).strip()

        elif ambito == EspacioUsuario.AMBITO_ESPACIO:
            espacio_id = attrs.get('espacio_id') if 'espacio_id' in attrs else (
                self.instance.espacio_id if self.instance else None
            )
            if not espacio_id:
                errors['espacio_id'] = 'Este campo es obligatorio.'

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
