from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    password = serializers.CharField(write_only = True)
    

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    