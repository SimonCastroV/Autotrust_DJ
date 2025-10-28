from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('vehicles', views.vehicle_list, name='vehicle_list'),
    path('subir/', views.upload_vehicle, name='upload_vehicle'),

]
