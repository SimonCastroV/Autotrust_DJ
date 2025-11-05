from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Min, Max
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import VehicleForm
from .models import Vehicle, VehicleImage, Venta


# ---------------- utils ----------------
def _to_decimal(value):
    try:
        return Decimal(value)
    except (TypeError, InvalidOperation):
        return None


# --------------- páginas informativas -----------------
def landing_page(request):
    return render(request, "home.html")


def why_autotrust(request):
    return render(request, "porque.html")


# --------------- listado + filtros -----------------
def vehicle_list(request):
    """
    Listado con filtros por marca, modelo y rango de precio.
    Renderiza: templates/vehicles/vehicle_list.html
    """
    qs = (
        Vehicle.objects
        .prefetch_related("imagenes")
        .all()
        .order_by("-fecha_publicacion")
    )

    # Filtros por querystring
    marca = (request.GET.get("marca") or "").strip()
    modelo = (request.GET.get("modelo") or "").strip()
    min_precio = _to_decimal(request.GET.get("min_precio"))
    max_precio = _to_decimal(request.GET.get("max_precio"))

    if marca:
        qs = qs.filter(marca__icontains=marca)
    if modelo:
        qs = qs.filter(modelo__icontains=modelo)
    if min_precio is not None:
        qs = qs.filter(precio__gte=min_precio)
    if max_precio is not None:
        qs = qs.filter(precio__lte=max_precio)

    # Límites para slider y lista de marcas
    agg = Vehicle.objects.aggregate(minp=Min("precio"), maxp=Max("precio"))
    minp = int(agg["minp"] or 0)
    maxp = int(agg["maxp"] or 100000000)

    marcas = (
        Vehicle.objects
        .exclude(marca__isnull=True)
        .exclude(marca__exact="")
        .values_list("marca", flat=True)
        .distinct()
        .order_by("marca")
    )

    # Paginación
    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "vehicles": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "paginator": paginator,
        "marcas": marcas,
        "min_precio_lim": minp,
        "max_precio_lim": maxp,
        "selected": {
            "marca": request.GET.get("marca", ""),
            "modelo": request.GET.get("modelo", ""),
            "min_precio": request.GET.get("min_precio", minp),
            "max_precio": request.GET.get("max_precio", maxp),
        },
    }
    return render(request, "vehicles/vehicle_list.html", context)


# --------------- subida de vehículos -----------------
@login_required
def upload_vehicle(request):
    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES)
        files = request.FILES.getlist("imagenes")

        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.usuario = request.user
            vehicle.save()

            for file_obj in files:
                VehicleImage.objects.create(vehicle=vehicle, imagen=file_obj)

            return redirect("catalogo")
    else:
        form = VehicleForm()

    return render(request, "vehicles/upload_vehicle.html", {"form": form})


# --------------- favoritos -----------------
@login_required
def toggle_favorite(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if vehicle.favoritos.filter(id=request.user.id).exists():
        vehicle.favoritos.remove(request.user)
    else:
        vehicle.favoritos.add(request.user)
    return redirect(request.META.get("HTTP_REFERER", "catalogo"))


# --------------- ventas -----------------
@login_required
def crear_venta(request, vehicle_id):
    """
    Crea una venta para el vehículo y redirige al recibo.
    """
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)

    # Tasa de impuesto configurable desde settings
    tasa = getattr(settings, "SALES_TAX", Decimal("0.19"))

    venta = Venta.objects.create(
        vehicle=vehicle,
        comprador=request.user,
        vendedor=vehicle.usuario,
        # snapshot del vehículo
        marca=vehicle.marca,
        modelo=vehicle.modelo,
        anio=vehicle.anio,
        ubicacion=vehicle.ubicacion,
        kilometraje=vehicle.kilometraje,
        motor=vehicle.motor,
        # montos
        precio_unitario=vehicle.precio,
        tasa_impuesto=tasa,
        metodo_pago="tarjeta",
    )
    return redirect("venta_recibo", venta_id=venta.id)


@login_required
def venta_recibo(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id)
    if not (request.user.is_staff or request.user == venta.comprador or request.user == venta.vendedor):
        return redirect("catalogo")
    return render(request, "vehicles/venta_recibo.html", {"venta": venta})


# --------------- API propia (JSON) -----------------
def vehicles_api(request):
    """
    Devuelve JSON con vehículos en venta.
    Incluye enlace directo al detalle y una imagen de portada si existe.
    """
    items = []
    queryset = Vehicle.objects.prefetch_related("imagenes").all().order_by("-fecha_publicacion")
    for vehicle in queryset:
        detalle_url = request.build_absolute_uri(reverse("vehicle_detail", args=[vehicle.pk]))

        if vehicle.imagenes.exists():
            img_url = request.build_absolute_uri(vehicle.imagenes.first().imagen.url)
        elif vehicle.imagen:
            img_url = request.build_absolute_uri(vehicle.imagen.url)
        else:
            img_url = None

        items.append({
            "id": vehicle.id,
            "marca": vehicle.marca,
            "modelo": vehicle.modelo,
            "anio": vehicle.anio,
            "precio": int(vehicle.precio),
            "ubicacion": vehicle.ubicacion,
            "kilometraje": vehicle.kilometraje,
            "motor": vehicle.motor,
            "detalle_url": detalle_url,
            "imagen_url": img_url,
        })
    return JsonResponse(items, safe=False, json_dumps_params={"ensure_ascii": False})


# --------------- detalle público -----------------
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle.objects.prefetch_related("imagenes"), pk=pk)
    return render(request, "vehicles/vehicle_detail.html", {"vehicle": vehicle})


# --------------- consumidor servicio aliado -----------------
def aliados_list(request):
    """
    Consume un servicio aliado (JSON) y lo muestra.
    Configura en settings.py la variable PARTNER_PRODUCTS_URL.
    """
    url = getattr(settings, "PARTNER_PRODUCTS_URL", None)
    data, error = [], None

    if not url:
        error = "Configura PARTNER_PRODUCTS_URL en settings.py"
    else:
        try:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                error = "El servicio aliado no devolvió una lista."
        except Exception as exc:
            error = f"Error al consumir el servicio aliado: {exc}"

    return render(request, "vehicles/aliados_list.html", {"items": data, "error": error})
