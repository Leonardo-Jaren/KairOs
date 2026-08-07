from django.urls import include, path
from rest_framework.routers import DefaultRouter

from equipos.views import ComponenteViewSet, EquipoViewSet

router = DefaultRouter()
router.register('componentes', ComponenteViewSet, basename='componente')
router.register('', EquipoViewSet, basename='equipo')

urlpatterns = [
    path('', include(router.urls)),
]
