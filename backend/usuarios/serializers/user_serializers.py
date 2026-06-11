from rest_framework import serializers
from usuarios.models import Usuario, PerfilTecnico

class PerfilTecnicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilTecnico
        fields = ["id_tecnico","area"]
        
class UsuarioReadSerializer(serializers.ModelSerializer):
    """
    Solo para lectura - respuestas GET
    """
    perfil_tecnico = PerfilTecnicoSerializer(read_only=True, default=None)
    
    class Meta:
        model = Usuario
        fields = ["id_usuario","perfil_tecnico","nombre","correo","rol","activo","created_at","updated_at"]
        
class UsuarioCreateSerializer(serializers.ModelSerializer):
    """
    Solo para creacion - POST /usuarios/
    """
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = Usuario
        fields = ["nombre","correo","password","rol"]
        extra_kwargs = {
            "correo": {"validators":[]}
        }
        
class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """
    Para actualizacion parcial - PATCH /usuarios/{id}/
    """
    password = serializers.CharField(
        write_only = True, 
        required = False, 
        min_length=8
    )
    
    class Meta:
        model = Usuario
        fields = ["nombre","correo","password","rol","activo"]
        extra_kwargs = {
              "nombre": {"required": False},
              "correo": {"required": False, "validators": []},
              "rol":    {"required": False},
              "activo": {"required": False},
          }
    

    

