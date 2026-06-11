from rest_framework.routers import DefaultRouter
from mantenimiento.views.mantenimiento_views import MantenimientoViewSet

router = DefaultRouter()
router.register('', MantenimientoViewSet, basename='mantenimiento')

urlpatterns = router.urls
