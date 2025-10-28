from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from vehicles import views
from django.shortcuts import redirect
from django.views.generic import RedirectView

urlpatterns = [
    path('', include('account.urls')),
    path('admin/', admin.site.urls),
    path('vehicles', include('vehicles.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
