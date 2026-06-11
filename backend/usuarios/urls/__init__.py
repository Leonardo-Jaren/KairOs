# usuarios/urls
# TODO: Implementar rutas para el módulo de usuarios

from django.urls import path, include

urlpatterns = [
    path("auth/", include("usuarios.urls.auth_urls")),
    path("", include("usuarios.urls.user_urls"))
]