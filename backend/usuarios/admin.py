from django.contrib import admin
from .models import Usuario, PerfilTecnico


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'id_usuario', 
        'nombre', 
        'correo', 
        'rol', 
        'activo',
        'created_at')
    list_filter = (
        'rol', 
        'activo',
        'created_at')
    search_fields = (
        'nombre', 
        'correo',)
    ordering = ('id_usuario',)
    readonly_fields = (
        'created_at',
        'updated_at')


@admin.register(PerfilTecnico)
class PerfilTecnicoAdmin(admin.ModelAdmin):
    list_display = (
        'id_tecnico', 
        'usuario', 
        'area')
    list_filter = ('area',)
    search_fields = (
        'usuario__nombre',
        'usuario__correo', 
        'area')
    ordering = ("id_tecnico",)
