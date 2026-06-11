from rest_framework.routers import DefaultRouter
from espacios.views.pabellon_views import PabellonViewSet

router = DefaultRouter()
router.register(r"", PabellonViewSet, basename="pabellon")

urlpatterns = router.urls
