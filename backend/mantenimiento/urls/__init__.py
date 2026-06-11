from django.urls import path, include

urlpatterns = [
    path('', include('mantenimiento.urls.mantenimiento_urls')),
]
