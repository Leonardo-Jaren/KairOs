from rest_framework.routers import DefaultRouter
from equipos.views.equipo_views import EquipoViewSet

router = DefaultRouter()
router.register(r"", EquipoViewSet, basename="equipo")

urlpatterns = router.urls
