from django.urls import path
from usuarios.views.auth_views import LoginView, LogoutView, TokenRefreshView

urlpatterns = [
      path("login/",         LoginView.as_view(),        name="auth-login"),
      path("logout/",        LogoutView.as_view(),        name="auth-logout"),
      path("token/refresh/", TokenRefreshView.as_view(),  name="auth-token-refresh"),
  ]