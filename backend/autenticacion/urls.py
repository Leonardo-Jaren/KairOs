from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from autenticacion.views.login_views import LocalLoginView, GoogleLoginView
from autenticacion.views.password_views import PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path('login/', LocalLoginView.as_view(), name='auth_login_local'),
    path('google/', GoogleLoginView.as_view(), name='auth_login_google'),
    path('refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'),
    
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
