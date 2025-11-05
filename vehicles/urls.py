from django.urls import path
from . import views

urlpatterns = [
    # Home / listado
    path("", views.vehicle_list, name="list"),
    path("vehicles/", views.vehicle_list, name="vehicle_list"),

    # CRUD / acciones propias
    path("subir/", views.upload_vehicle, name="upload_vehicle"),
    path("favorito/<int:vehicle_id>/", views.toggle_favorite, name="toggle_favorite"),

    # Ventas / recibo
    path("ventas/crear/<int:vehicle_id>/", views.crear_venta, name="crear_venta"),
    path("ventas/<int:venta_id>/recibo/", views.venta_recibo, name="venta_recibo"),

    # servicio JSON proveedor + detalle para enlaces públicos
    path("api/vehicles/", views.vehicles_api, name="vehicles_api"),
    path("vehiculo/<int:pk>/", views.vehicle_detail, name="vehicle_detail"),

    # consumidor de servicio aliado
    path("aliados/", views.aliados_list, name="aliados_list"),
]
