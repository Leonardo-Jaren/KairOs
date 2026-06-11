from rest_framework.routers import DefaultRouter
from usuarios.views.user_views import UsuarioViewSet

router = DefaultRouter()
router.register(r"", UsuarioViewSet, basename="usuario")

urlpatterns = router.urls