<<<<<<< HEAD
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max
from django.core.paginator import Paginator
from decimal import Decimal, InvalidOperation
from django.conf import settings

from .forms import VehicleForm
from .models import Vehicle, VehicleImage, Venta



# ---------------- utils ----------------
def _to_decimal(v):
    try:
        return Decimal(v)
    except (TypeError, InvalidOperation):
        return None


# --------------- views -----------------
def landing_page(request):
    return render(request, "home.html")


def why_autotrust(request):
    return render(request, "porque.html")


def vehicle_list(request):
    """
    Listado con filtros por marca, modelo y rango de precio.
    Renderiza: templates/vehicles/vehicle_list.html
    """
    # Base queryset con imágenes (y orden por fecha)
    qs = (
        Vehicle.objects
        .prefetch_related("imagenes")
        .all()
        .order_by("-fecha_publicacion")
    )

    # -------- Filtros por querystring --------
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

    # -------- Datos para el slider y el select de marcas --------
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

    # -------- Paginación (opcional) --------
    paginator = Paginator(qs, 12)  # 12 items por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "vehicles": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "paginator": paginator,

        # contexto requerido por el template con filtros/slider:
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


@login_required
def upload_vehicle(request):
    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES)
        files = request.FILES.getlist("imagenes")

        if form.is_valid():
            # Creamos el vehículo pero aún no lo guardamos
            vehicle = form.save(commit=False)
            vehicle.usuario = request.user  # Asociar al usuario logueado
            vehicle.save()

            # Guardar imágenes adicionales si las hay
            for f in files:
                VehicleImage.objects.create(vehicle=vehicle, imagen=f)

            return redirect("catalogo")
    else:
        form = VehicleForm()

    return render(request, "vehicles/upload_vehicle.html", {"form": form})


@login_required
def toggle_favorite(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if vehicle.favoritos.filter(id=request.user.id).exists():
        vehicle.favoritos.remove(request.user)
    else:
        vehicle.favoritos.add(request.user)
    return redirect(request.META.get("HTTP_REFERER", "catalogo"))

@login_required
def crear_venta(request, vehicle_id):
    """
    Crea una venta para el vehículo y redirige al recibo.
    Por simplicidad, se crea al instante (podrías pedir confirmación en otra vista si quieres).
    """
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)

    # Tasa de impuesto configurable desde settings (opcional)
    tasa = getattr(settings, "SALES_TAX", Decimal("0.19"))

    venta = Venta.objects.create(
        vehicle=vehicle,
        comprador=request.user,
        vendedor=vehicle.usuario,
        # snapshot
        marca=vehicle.marca,
        modelo=vehicle.modelo,
        anio=vehicle.anio,
        ubicacion=vehicle.ubicacion,
        kilometraje=vehicle.kilometraje,
        motor=vehicle.motor,
        # montos
        precio_unitario=vehicle.precio,
        tasa_impuesto=tasa,
        metodo_pago="tarjeta",  # o detectar desde un form si más adelante agregas
    )

    return redirect("venta_recibo", venta_id=venta.id)


@login_required
def venta_recibo(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id)
    # Solo comprador o staff puede ver
    if not (request.user.is_staff or request.user == venta.comprador):
        return redirect("catalogo")

    context = {
        "venta": venta,
    }
    return render(request, "vehicles/venta_recibo.html", context)
=======
# vehicles/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max
from django.core.paginator import Paginator
from decimal import Decimal, InvalidOperation
import requests

from .forms import VehicleForm
from .models import Vehicle, VehicleImage, Venta


# ---------------- utils ----------------
def _to_decimal(v):
    try:
        return Decimal(v)
    except (TypeError, InvalidOperation):
        return None


# --------------- LISTADO + FILTROS -----------------
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


# --------------- UPLOAD -----------------
@login_required
def upload_vehicle(request):
    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES)
        files = request.FILES.getlist("imagenes")

        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.usuario = request.user
            vehicle.save()

            for f in files:
                VehicleImage.objects.create(vehicle=vehicle, imagen=f)

            return redirect("vehicle_list")
    else:
        form = VehicleForm()

    return render(request, "vehicles/upload_vehicle.html", {"form": form})


# --------------- FAVORITOS -----------------
@login_required
def toggle_favorite(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if vehicle.favoritos.filter(id=request.user.id).exists():
        vehicle.favoritos.remove(request.user)
    else:
        vehicle.favoritos.add(request.user)
    return redirect(request.META.get("HTTP_REFERER", "vehicle_list"))


# --------------- VENTAS -----------------
@login_required
def crear_venta(request, vehicle_id):
    """
    Crea una venta para el vehículo y redirige al recibo.
    """
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)

    # Tasa de impuesto configurable desde settings (opcional)
    tasa = getattr(settings, "SALES_TAX", Decimal("0.19"))

    venta = Venta.objects.create(
        vehicle=vehicle,
        comprador=request.user,
        vendedor=vehicle.usuario,  # puede ser None si no se asignó; tu modelo lo permite
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
    # Solo comprador, vendedor o staff pueden ver
    if not (request.user.is_staff or request.user == venta.comprador or request.user == venta.vendedor):
        return redirect("vehicle_list")
    return render(request, "vehicles/venta_recibo.html", {"venta": venta})


# --------------- API PROPIA (JSON) -----------------
def vehicles_api(request):
    """
    Devuelve JSON con vehículos en venta.
    Incluye enlace directo al detalle y una imagen de portada si existe.
    """
    items = []
    for v in Vehicle.objects.prefetch_related("imagenes").all().order_by("-fecha_publicacion"):
        detalle_url = request.build_absolute_uri(reverse("vehicle_detail", args=[v.pk]))
        # imagen de portada
        if v.imagenes.exists():
            img_url = request.build_absolute_uri(v.imagenes.first().imagen.url)
        elif v.imagen:
            img_url = request.build_absolute_uri(v.imagen.url)
        else:
            img_url = None

        items.append({
            "id": v.id,
            "marca": v.marca,
            "modelo": v.modelo,
            "anio": v.anio,
            "precio": int(v.precio),
            "ubicacion": v.ubicacion,
            "kilometraje": v.kilometraje,
            "motor": v.motor,
            "detalle_url": detalle_url,
            "imagen_url": img_url,
        })
    return JsonResponse(items, safe=False, json_dumps_params={"ensure_ascii": False})


# --------------- DETALLE PARA ENLACE PÚBLICO -----------------
def vehicle_detail(request, pk):
    v = get_object_or_404(Vehicle.objects.prefetch_related("imagenes"), pk=pk)
    return render(request, "vehicles/vehicle_detail.html", {"vehicle": v})


# --------------- CONSUMIDOR SERVICIO ALIADO -----------------
def aliados_list(request):
    """
    Consume un servicio aliado (JSON) y lo muestra.
    Configura en settings.py:
      PARTNER_PRODUCTS_URL = "https://equipo2.ejemplo/api/productos/"
    Se espera una lista de objetos (flexible): nombre/titulo, precio, detalle_url, imagen_url, etc.
    """
    url = getattr(settings, "PARTNER_PRODUCTS_URL", None)
    data, error = [], None

    if not url:
        error = "Configura PARTNER_PRODUCTS_URL en settings.py"
    else:
        try:
            resp = requests.get(url, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list):
                error = "El servicio aliado no devolvió una lista."
        except Exception as e:
            error = f"Error al consumir el servicio aliado: {e}"

    return render(request, "vehicles/aliados_list.html", {"items": data, "error": error})
>>>>>>> 5f9d7e80559e6c5ae73585796cc9ca98f72c5bd6
