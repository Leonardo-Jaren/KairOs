from django.urls import include, path
from rest_framework.routers import DefaultRouter

from espacios.views import EspacioUsuarioViewSet, EspacioViewSet

router = DefaultRouter()
router.register('usuarios', EspacioUsuarioViewSet, basename='espacio-usuario')
router.register('', EspacioViewSet, basename='espacio')

urlpatterns = [
    path('', include(router.urls)),
]
