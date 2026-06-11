from django.urls import path, include

urlpatterns = [
    path("pabellones/", include("espacios.urls.pabellon_urls")),
    path("",            include("espacios.urls.espacio_urls")),
]
