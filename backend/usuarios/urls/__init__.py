from django.urls import path, include
from rest_framework.routers import DefaultRouter

from usuarios.views import UsuarioViewSet

router = DefaultRouter()
router.register('', UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
]

