from django.urls import include, path
from rest_framework.routers import DefaultRouter

from equipos.views import EquipoViewSet

router = DefaultRouter()
router.register('', EquipoViewSet, basename='equipo')

urlpatterns = [
    path('', include(router.urls)),
]
