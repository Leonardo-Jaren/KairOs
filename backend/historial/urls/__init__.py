from django.urls import include, path
from rest_framework.routers import DefaultRouter

from historial.views import HistorialViewSet

router = DefaultRouter()
router.register('', HistorialViewSet, basename='historial')

urlpatterns = [
    path('', include(router.urls)),
]
