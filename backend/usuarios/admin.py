from django.contrib import admin
from .models import Usuario, PerfilTecnico


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'nombre', 'correo', 'rol', 'is_active')
    list_filter = ('rol', 'is_active')
    search_fields = ('nombre', 'correo', 'username')
    ordering = ('id',)


@admin.register(PerfilTecnico)
class PerfilTecnicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'area')
    list_filter = ('area',)
    search_fields = ('usuario__nombre', 'area')
