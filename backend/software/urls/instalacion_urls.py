from rest_framework.routers import DefaultRouter
from software.views.instalacion_views import InstalacionViewSet

router = DefaultRouter()
router.register(r"", InstalacionViewSet, basename="instalacion")

urlpatterns = router.urls
