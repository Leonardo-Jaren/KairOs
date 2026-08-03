from django.urls import include, path
from rest_framework.routers import DefaultRouter

from mantenimiento.views import MantenimientoViewSet

router = DefaultRouter()
router.register('', MantenimientoViewSet, basename='mantenimiento')

urlpatterns = [
    path('', include(router.urls)),
]
