from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from vehicles.models import Vehicle, Venta

class VentaModelTests(TestCase):
    def setUp(self):
        self.vendedor = User.objects.create_user(username="seller", password="pass")
        self.comprador = User.objects.create_user(username="buyer", password="pass")

        self.vehicle = Vehicle.objects.create(
            usuario=self.vendedor,
            marca="Toyota",
            modelo="Corolla",
            anio="2020",
            precio=Decimal("50000000"),
            ubicacion="Antioquia",
            kilometraje=10000,
            motor="1.8",
        )

    def test_crea_venta_y_calcula_totales(self):
        venta = Venta.objects.create(
            vehicle=self.vehicle,
            comprador=self.comprador,
            vendedor=self.vendedor,
            marca=self.vehicle.marca,
            modelo=self.vehicle.modelo,
            anio=self.vehicle.anio,
            ubicacion=self.vehicle.ubicacion,
            kilometraje=self.vehicle.kilometraje,
            motor=self.vehicle.motor,
            precio_unitario=self.vehicle.precio,
            tasa_impuesto=Decimal("0.19"),
            metodo_pago="tarjeta",
        )
        # Subtotal = precio_unitario
        self.assertEqual(venta.subtotal, Decimal("50000000"))
        # Impuesto = round(subtotal * tasa_impuesto)
        self.assertEqual(venta.impuesto, (Decimal("50000000") * Decimal("0.19")).quantize(Decimal("1")))
        # Total = subtotal + impuesto (redondeado a entero)
        self.assertEqual(venta.total, (venta.subtotal + venta.impuesto))
        # Folio autogenerado
        self.assertTrue(venta.folio and isinstance(venta.folio, str))
        self.assertGreaterEqual(len(venta.folio), 8)
