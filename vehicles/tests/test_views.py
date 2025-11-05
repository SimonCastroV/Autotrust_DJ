# vehicles/tests/test_views.py
from decimal import Decimal
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from vehicles.models import Vehicle, Venta
import tempfile

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class VehicleViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.seller = User.objects.create_user(username="seller", password="pass")
        cls.buyer  = User.objects.create_user(username="buyer",  password="pass")
        cls.other  = User.objects.create_user(username="other",  password="pass")

        cls.v1 = Vehicle.objects.create(
            usuario=cls.seller, marca="Mazda", modelo="CX-5", anio="2022",
            precio=Decimal("120000000"), ubicacion="Bogotá", kilometraje=5000, motor="2.5"
        )
        cls.v2 = Vehicle.objects.create(
            usuario=cls.seller, marca="Toyota", modelo="Corolla", anio="2020",
            precio=Decimal("50000000"), ubicacion="Medellín", kilometraje=12000, motor="1.8"
        )

    def test_listado_sin_filtros_muestra_todos(self):
        res = self.client.get(reverse("vehicle_list"))
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.context["vehicles"]), 2)

    def test_filtra_por_marca(self):
        res = self.client.get(reverse("vehicle_list"), {"marca": "Toyota"})
        ids = {v.id for v in res.context["vehicles"]}
        self.assertIn(self.v2.id, ids)
        self.assertNotIn(self.v1.id, ids)

    def test_filtra_por_modelo(self):
        res = self.client.get(reverse("vehicle_list"), {"modelo": "CX-5"})
        ids = {v.id for v in res.context["vehicles"]}
        self.assertIn(self.v1.id, ids)
        self.assertNotIn(self.v2.id, ids)

    def test_filtra_por_rango_precio(self):
        res = self.client.get(reverse("vehicle_list"),
                              {"min_precio": "60000000", "max_precio": "200000000"})
        ids = {v.id for v in res.context["vehicles"]}
        self.assertIn(self.v1.id, ids)
        self.assertNotIn(self.v2.id, ids)

    def test_crear_venta_requiere_login(self):
        res = self.client.post(reverse("crear_venta", args=[self.v2.id]))
        self.assertEqual(res.status_code, 302)  # redirige a login

    def test_crear_venta_ok_y_redirige_recibo(self):
        self.client.login(username="buyer", password="pass")
        res = self.client.post(reverse("crear_venta", args=[self.v2.id]))
        self.assertEqual(res.status_code, 302)
        venta = Venta.objects.first()
        self.assertEqual(venta.vehicle, self.v2)
        self.assertIn(reverse("venta_recibo", args=[venta.id]), res["Location"])

    def test_recibo_solo_comprador_o_staff(self):
        self.client.login(username="buyer", password="pass")
        self.client.post(reverse("crear_venta", args=[self.v2.id]))
        venta = Venta.objects.first()

        # comprador puede ver
        self.assertEqual(self.client.get(reverse("venta_recibo", args=[venta.id])).status_code, 200)

        # otro usuario no
        self.client.logout()
        self.client.login(username="other", password="pass")
        res = self.client.get(reverse("venta_recibo", args=[venta.id]))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("vehicle_list"))

        # staff sí
        self.client.logout()
        self.other.is_staff = True
        self.other.save()
        self.client.login(username="other", password="pass")
        self.assertEqual(self.client.get(reverse("venta_recibo", args=[venta.id])).status_code, 200)
