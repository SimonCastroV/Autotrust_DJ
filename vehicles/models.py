from django.db import models
from django.utils import timezone

class Vehicle(models.Model):
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    anio = models.CharField(max_length=10)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=12, decimal_places=0)
    ubicacion = models.CharField(max_length=100, default="Antioquia")
    kilometraje = models.IntegerField(default=0)
    motor = models.CharField(max_length=50, blank=True, null=True)
    imagen = models.ImageField(upload_to='vehiculos/', blank=True, null=True)
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.marca} {self.modelo}"

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='vehiculos/galeria/')

    def __str__(self):
        return f"Imagen de {self.vehicle.marca} {self.vehicle.modelo}"
