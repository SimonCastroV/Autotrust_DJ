from django.urls import path
from . import views

urlpatterns = [
    path("", views.vehicle_list, name="list"),                 # Home
    path("vehicles/", views.vehicle_list, name="vehicle_list"),# /vehicles
    path("subir/", views.upload_vehicle, name="upload_vehicle"),
    path("favorito/<int:vehicle_id>/", views.toggle_favorite, name="toggle_favorite"),
]
