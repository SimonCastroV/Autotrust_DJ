# vehicles/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal

class Vehicle(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vehiculos_publicados",
        null=True,
        blank=True
    )
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
    favoritos = models.ManyToManyField(User, related_name='vehiculos_favoritos', blank=True)

    def __str__(self):
        return f"{self.marca} {self.modelo}"


class VehicleImage(models.Model):
    # usar string evita problemas de importación circular
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='vehiculos/galeria/')

    def __str__(self):
        return f"Imagen de {self.vehicle.marca} {self.vehicle.modelo}"


class Venta(models.Model):
    METODOS_PAGO = [
        ("tarjeta", "Tarjeta"),
        ("transferencia", "Transferencia"),
        ("efectivo", "Efectivo"),
        ("otro", "Otro"),
    ]

    # Relaciones
    vehicle   = models.ForeignKey("Vehicle", on_delete=models.PROTECT, related_name="ventas")
    comprador = models.ForeignKey(User, on_delete=models.PROTECT, related_name="compras")
    vendedor  = models.ForeignKey(User, on_delete=models.PROTECT, related_name="ventas_realizadas", null=True, blank=True)

    # Snapshot del vehículo (para que el recibo no cambie si luego editan el vehículo)
    marca       = models.CharField(max_length=100)
    modelo      = models.CharField(max_length=100)
    anio        = models.CharField(max_length=10)
    ubicacion   = models.CharField(max_length=100)
    kilometraje = models.IntegerField(default=0)
    motor       = models.CharField(max_length=50, blank=True, null=True)

    # Montos
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=0)
    impuesto        = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total           = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    # 19% por defecto; puedes cambiarlo desde settings.SALES_TAX en la vista
    tasa_impuesto   = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.19"))

    # Otros
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default="tarjeta")
    folio       = models.CharField(max_length=30, unique=True, blank=True)  # N° de recibo
    creado_en   = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-creado_en",)

    def __str__(self):
        return f"Recibo {self.folio or '—'} • {self.marca} {self.modelo}"

    # ---- Propiedades esperadas por los tests ----
    @property
    def subtotal(self) -> Decimal:
        # como precio_unitario ya es entero (decimal_places=0), lo normalizamos por claridad
        return Decimal(self.precio_unitario).quantize(Decimal("1"))

    # impuesto y total son campos en BD; los calculamos antes de guardar
    # --------------------------------------------------------------

    def calcular_montos(self):
        """
        Calcula impuesto y total a partir de precio_unitario y tasa_impuesto.
        Redondea a enteros (quantize a '1') para consistencia con los tests.
        """
        self.impuesto = (Decimal(self.precio_unitario) * Decimal(self.tasa_impuesto)).quantize(Decimal("1"))
        self.total    = (Decimal(self.precio_unitario) + self.impuesto).quantize(Decimal("1"))

    def save(self, *args, **kwargs):
        # Calcular montos si vienen vacíos o si alguno está en None
        if not self.impuesto or not self.total:
            self.calcular_montos()

        # Generar folio único si no existe (formato: V-YYYY-000123)
        if not self.folio:
            base = timezone.now().strftime("V-%Y-")
            # Primer guardado para obtener pk
            super().save(*args, **kwargs)
            self.folio = f"{base}{self.pk:06d}"
            # Asegurar que el siguiente save sea update
            kwargs["force_insert"] = False

        # Guardado final (o único si ya había folio)
        super().save(*args, **kwargs)
