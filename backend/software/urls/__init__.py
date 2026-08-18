from django.urls import include, path
from rest_framework.routers import DefaultRouter

from software.views import ProductoSoftwareViewSet, SoftwareInstaladoViewSet

router = DefaultRouter()
router.register(
    'productos',
    ProductoSoftwareViewSet,
    basename='producto-software',
)
router.register(
    'instalaciones',
    SoftwareInstaladoViewSet,
    basename='software-instalado',
)

urlpatterns = [
    path('', include(router.urls)),
]
