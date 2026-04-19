from rest_framework import serializers
from historial.models import Historial

# -- Seralizer para lectura (GET) 
class HistorialSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura.
    Expone datos anidados legibles del equipo y mantenimiento asociado.
    """
    equipo_codigo  = serializers.CharField(
        source='id_equipo_fk.codigo', 
        read_only=True
        )
    mantenimiento_tipo = serializers.CharField(
        source='id_mantenimiento_fk.tipo_mantenimiento', 
        read_only=True,
        default=None
        )
    
    class Meta:
        model = Historial
        fields = [
            'id_historial',
            'id_equipo_fk',
            'equipo_codigo',
            'id_mantenimiento_fk',
            'mantenimiento_tipo',
            'fecha',
            'descripcion'
        ]
        read_only_fields = fields 

# -- Serializer de escritura (POST / PUT / PATCH)  
class HistorialWriteSerializer(serializers.ModelSerializer):
    """
    Serializer de escritura.
    Recibe solo IDs de las FK y valida su existencia antes de guardar.
    """
    class Meta:
        model = Historial 
        fields = [
            'id_equipo_fk',
            'id_mantenimiento_fk',
            'fecha',
            'descripcion'
        ]

        def validate_id_equipo_fk(self, value):
            if value is None:
                raise serializers.ValidationError("El equipo es obligatorio.")
            return value
        
        def validate_descripcion(self, value):
            if not value or not value.strip():
                raise serializers.ValidationError("La descripción no puede estar vacía.")
            return value.strip()
        
        def validate(self, attrs):
           """Validación cruzada de campos."""
           fecha = attrs.get('fecha')
           if fecha is None:
               raise serializers.ValidationError({"fecha":"La fecha es obligatoria."}) 
           return attrs 
        
