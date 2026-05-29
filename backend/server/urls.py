"""
URL configuration for KairOs backend project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('autenticacion.urls')),
    path('api/v1/usuarios/', include('usuarios.urls')),
    # TODO: Descomentar conforme se implementen las urls de cada módulo
    # path('api/v1/espacios/', include('espacios.urls')),
    # path('api/v1/equipos/', include('equipos.urls')),
    # path('api/v1/software/', include('software.urls')),
    # path('api/v1/mantenimiento/', include('mantenimiento.urls')),
    # path('api/v1/incidencias/', include('incidencias.urls')),
    # path('api/v1/historial/', include('historial.urls')),
]
