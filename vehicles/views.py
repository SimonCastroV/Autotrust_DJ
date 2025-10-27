from django.shortcuts import render, redirect
from .forms import VehicleForm
from .models import Vehicle,VehicleImage

def vehicle_list(request):
    vehicles = Vehicle.objects.prefetch_related('imagenes').all()
    return render(request, "vehicles/vehicle_list.html", {"vehicles": vehicles})

def upload_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save()
            # guardar imágenes adicionales
            imagenes = request.FILES.getlist('imagenes')
            for img in imagenes:
                VehicleImage.objects.create(vehicle=vehicle, imagen=img)
            return redirect('vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'vehicles/upload_vehicle.html', {'form': form})