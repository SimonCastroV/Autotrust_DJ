from django.contrib import admin
from .models import Vehicle, VehicleImage, Venta

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("marca", "modelo", "anio", "precio", "ubicacion")

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("folio", "marca", "modelo", "precio_unitario", "impuesto", "total", "comprador", "vendedor", "creado_en")
    search_fields = ("folio", "marca", "modelo", "comprador__username", "vendedor__username")
    list_filter = ("metodo_pago", "tasa_impuesto", "creado_en")
