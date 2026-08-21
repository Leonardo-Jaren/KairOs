from django.urls import include, path
from rest_framework.routers import DefaultRouter

from incidencias.views import IncidenciaViewSet

router = DefaultRouter()
router.register('', IncidenciaViewSet, basename='incidencia')

urlpatterns = [
    path('', include(router.urls)),
]
