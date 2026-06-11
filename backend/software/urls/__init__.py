from django.urls import path, include

urlpatterns = [
    path("productos/",     include("software.urls.producto_urls")),
    path("instalaciones/", include("software.urls.instalacion_urls")),
]
