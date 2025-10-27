from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehicle_list, name='vehicle_list'),
    path('subir/', views.upload_vehicle, name='upload_vehicle'),
]
