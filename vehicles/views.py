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

            return redirect("vehicle_list")
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
    return redirect(request.META.get("HTTP_REFERER", "vehicle_list"))

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
        return redirect("vehicle_list")

    context = {
        "venta": venta,
    }
    return render(request, "vehicles/venta_recibo.html", context)
