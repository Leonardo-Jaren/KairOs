from rest_framework.routers import DefaultRouter
from espacios.views.espacio_views import EspacioViewSet

router = DefaultRouter()
router.register(r"", EspacioViewSet, basename="espacio")

urlpatterns = router.urls
