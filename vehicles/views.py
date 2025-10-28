from django.shortcuts import render, redirect, get_object_or_404
from .forms import VehicleForm
from .models import Vehicle,VehicleImage
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def vehicle_list(request):
    vehicles = Vehicle.objects.prefetch_related('imagenes').all()
    return render(request, "vehicles/vehicle_list.html", {"vehicles": vehicles})

@login_required
def upload_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        files = request.FILES.getlist('imagenes')

        if form.is_valid():
            # Creamos el vehículo pero aún no lo guardamos
            vehicle = form.save(commit=False)
            vehicle.usuario = request.user  # 🔹 Asociamos el vehículo al usuario logueado
            vehicle.save()

            # 🔹 Guardamos las imágenes adicionales si las hay
            for f in files:
                VehicleImage.objects.create(vehicle=vehicle, imagen=f)

            return redirect('vehicle_list')
    else:
        form = VehicleForm()

    return render(request, 'vehicles/upload_vehicle.html', {'form': form})

@login_required
def toggle_favorite(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if vehicle.favoritos.filter(id=request.user.id).exists():
        vehicle.favoritos.remove(request.user)
    else:
        vehicle.favoritos.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'vehicle_list'))


