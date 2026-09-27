from django.urls import include, path
from rest_framework.routers import DefaultRouter

from espacios.views import (
    CiudadViewSet,
    EdificioViewSet,
    EspacioUsuarioViewSet,
    EspacioViewSet,
    LocalViewSet,
)

router = DefaultRouter()
router.register('ciudades', CiudadViewSet, basename='ciudad')
router.register('usuarios', EspacioUsuarioViewSet, basename='espacio-usuario')
router.register('edificios', EdificioViewSet, basename='edificio')
router.register('locales', LocalViewSet, basename='local')
router.register('', EspacioViewSet, basename='espacio')

urlpatterns = [
    path('', include(router.urls)),
]
