from rest_framework.routers import DefaultRouter
from equipos.views.componente_views import ComponenteViewSet

router = DefaultRouter()
router.register(r"", ComponenteViewSet, basename="componente")

urlpatterns = router.urls
