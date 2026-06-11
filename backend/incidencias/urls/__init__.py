from django.urls import path, include

urlpatterns = [
    path('', include('incidencias.urls.incidencia_urls')),
]
