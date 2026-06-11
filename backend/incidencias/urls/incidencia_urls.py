from rest_framework.routers import DefaultRouter
from incidencias.views.incidencia_views import IncidenciaViewSet

router = DefaultRouter()
router.register('', IncidenciaViewSet, basename='incidencia')

urlpatterns = router.urls
