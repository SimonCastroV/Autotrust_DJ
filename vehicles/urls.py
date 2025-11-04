from django.urls import path
from . import views

urlpatterns = [
    path("", views.vehicle_list, name="list"),                 # Home
    path("vehicles/", views.vehicle_list, name="vehicle_list"),# /vehicles
    path("subir/", views.upload_vehicle, name="upload_vehicle"),
    path("favorito/<int:vehicle_id>/", views.toggle_favorite, name="toggle_favorite"),
    path("ventas/crear/<int:vehicle_id>/", views.crear_venta, name="crear_venta"),
path("ventas/<int:venta_id>/recibo/", views.venta_recibo, name="venta_recibo"),
]
