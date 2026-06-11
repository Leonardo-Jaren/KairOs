from django.urls import path, include

urlpatterns = [
    path('', include('historial.urls.historial_urls')),
]
