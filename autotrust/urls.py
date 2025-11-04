from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("account.urls")),   # si usas auth propia
    path("admin/", admin.site.urls),
    path("", include("vehicles.urls")),  # expone /, /vehicles/, /subir/, /favorito/...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
