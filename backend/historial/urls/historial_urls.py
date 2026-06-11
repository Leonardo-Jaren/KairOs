from rest_framework.routers import DefaultRouter
from historial.views.historial_views import HistorialViewSet

router = DefaultRouter()
router.register('', HistorialViewSet, basename='historial')

urlpatterns = router.urls
