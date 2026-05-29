from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from autenticacion.views import LocalLoginView, GoogleLoginView

urlpatterns = [
    path('login/', LocalLoginView.as_view(), name='auth_login_local'),
    path('google/', GoogleLoginView.as_view(), name='auth_login_google'),
    path('refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'),
]
