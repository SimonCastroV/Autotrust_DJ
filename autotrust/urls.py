from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("vehicles.urls")),  # landing + catálogo
    path("admin/", admin.site.urls),
    path("", include("account.urls")),   # login, registro, perfil
    path("chatt/", include("chatt.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
