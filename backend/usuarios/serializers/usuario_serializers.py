from rest_framework import serializers

from usuarios.models import Usuario


class SupervisorSummarySerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'apellido', 'nombre_completo', 'rol']

    def get_nombre_completo(self, obj: Usuario) -> str:
        return f'{obj.nombre} {obj.apellido}'.strip()


class UsuarioSerializer(serializers.ModelSerializer):
    """Representa datos públicos de una cuenta sin campos sensibles."""

    nombre_completo = serializers.SerializerMethodField()
    supervisor_id = serializers.SerializerMethodField()
    supervisor = serializers.SerializerMethodField()
    sedes = serializers.SerializerMethodField()
    subordinados_count = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'correo',
            'nombre',
            'apellido',
            'nombre_completo',
            'dni',
            'rol',
            'supervisor_id',
            'supervisor',
            'sedes',
            'subordinados_count',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_nombre_completo(self, obj: Usuario) -> str:
        """Combina nombre y apellido para su presentación en tablas."""
        return f'{obj.nombre} {obj.apellido}'.strip()

    def get_supervisor_id(self, obj: Usuario) -> int | None:
        """Los docentes no tienen supervisor dentro de la jerarquía institucional."""
        return None if obj.rol == 'docente' else obj.supervisor_id

    def get_supervisor(self, obj: Usuario) -> dict | None:
        """Oculta relaciones heredadas que ya no aplican a docentes."""
        if obj.rol == 'docente' or not obj.supervisor:
            return None
        return SupervisorSummarySerializer(obj.supervisor).data

    def get_sedes(self, obj: Usuario) -> list:
        """Entrega las sedes físicas asignadas y su condición de sede principal."""
        return [
            {
                'id': us.local.id,
                'codigo': us.local.codigo,
                'nombre': us.local.nombre,
                'ciudad': us.local.ciudad,
                'es_sede_principal': us.es_sede_principal,
                'activo': us.activo,
            }
            for us in obj.usuario_sedes.all()
            if us.activo and hasattr(us, 'local') and us.local
        ]

    def get_subordinados_count(self, obj: Usuario) -> int:
        """Cuenta subordinados directos activos."""
        if hasattr(obj, 'subordinados_activos_count'):
            return obj.subordinados_activos_count
        return obj.subordinados.filter(is_active=True).count()



class UsuarioCreateUpdateSerializer(serializers.ModelSerializer):
    """Valida el formato de los datos de escritura de usuarios."""

    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        trim_whitespace=False,
        style={'input_type': 'password'},
    )
    supervisor_id = serializers.IntegerField(required=False, allow_null=True)
    sede_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True,
    )
    sede_principal_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'correo',
            'nombre',
            'apellido',
            'dni',
            'rol',
            'password',
            'is_active',
            'supervisor_id',
            'sede_ids',
            'sede_principal_id',
        ]
        extra_kwargs = {
            'correo': {'validators': []},
            'username': {'validators': []},
        }

    def validate_correo(self, value: str) -> str:
        """Normaliza el correo antes de delegar su unicidad al service."""
        return value.strip().lower()

    def validate_dni(self, value: str | None) -> str | None:
        """Acepta únicamente DNI peruanos de ocho dígitos."""
        if value and (len(value) != 8 or not value.isdigit()):
            raise serializers.ValidationError('El DNI debe contener 8 dígitos.')
        return value


class PermisoItemSerializer(serializers.Serializer):
    modulo = serializers.CharField(max_length=50)
    accion = serializers.CharField(max_length=20)
    permitido = serializers.BooleanField()


class GuardarPermisosSerializer(serializers.Serializer):
    permisos = PermisoItemSerializer(many=True, required=False, default=list)
    reset_to_default = serializers.BooleanField(required=False, default=False)

