from rest_framework.routers import DefaultRouter
from software.views.producto_views import ProductoSoftwareViewSet

router = DefaultRouter()
router.register(r"", ProductoSoftwareViewSet, basename="producto-software")

urlpatterns = router.urls
