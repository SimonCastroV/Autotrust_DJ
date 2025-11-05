from django.urls import path

from . import views

urlpatterns = [
    # Landing y contenido informativo
    path("", views.landing_page, name="landing"),
    path("porque/", views.why_autotrust, name="porque"),

    # Catálogo / listado
    path("catalogo/", views.vehicle_list, name="catalogo"),
    path("vehicles/", views.vehicle_list, name="vehicle_list"),

    # CRUD / acciones de usuario
    path("subir/", views.upload_vehicle, name="upload_vehicle"),
    path("favorito/<int:vehicle_id>/", views.toggle_favorite, name="toggle_favorite"),

    # Ventas / recibos
    path("ventas/crear/<int:vehicle_id>/", views.crear_venta, name="crear_venta"),
    path("ventas/<int:venta_id>/recibo/", views.venta_recibo, name="venta_recibo"),

    # API y servicios
    path("api/vehicles/", views.vehicles_api, name="vehicles_api"),
    path("vehiculo/<int:pk>/", views.vehicle_detail, name="vehicle_detail"),
    path("aliados/", views.aliados_list, name="aliados_list"),
]
