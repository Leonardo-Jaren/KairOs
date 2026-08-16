from django.urls import include, path
from rest_framework.routers import DefaultRouter

from software.views import ProductoSoftwareViewSet, SoftwareInstaladoViewSet

router = DefaultRouter()
router.register('instalaciones', SoftwareInstaladoViewSet, basename='software-instalado')
router.register('productos', ProductoSoftwareViewSet, basename='producto-software')

urlpatterns = [
    path('', include(router.urls)),
]
