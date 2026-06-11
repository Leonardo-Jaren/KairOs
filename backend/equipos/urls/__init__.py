from django.urls import path, include

urlpatterns = [
    path("componentes/", include("equipos.urls.componente_urls")),
    path("",             include("equipos.urls.equipo_urls")),
]
