from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from finanzas.forms import TransferenciaForm
from finanzas.models import Categoria, Transferencia, Transaccion


class SecurityAndTransferTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.other_user = User.objects.create_user(username="bob", password="password123")

        self.ingreso_categoria = (
            Categoria.objects.filter(usuario=self.user, tipo="ingreso", nombre="Salario").first()
            or Categoria.objects.filter(usuario=self.user, tipo="ingreso").first()
        )
        self.gasto_categoria = (
            Categoria.objects.filter(usuario=self.user, tipo="gasto", nombre="Compras").first()
            or Categoria.objects.filter(usuario=self.user, tipo="gasto").first()
        )
        if self.ingreso_categoria is None:
            self.ingreso_categoria = Categoria.objects.create(
                usuario=self.user,
                nombre="Salario",
                tipo="ingreso",
            )
        if self.gasto_categoria is None:
            self.gasto_categoria = Categoria.objects.create(
                usuario=self.user,
                nombre="Compras",
                tipo="gasto",
            )

        Transaccion.objects.create(
            usuario=self.user,
            tipo="ingreso",
            monto=1000,
            categoria=self.ingreso_categoria,
        )

    def test_authenticated_pages_are_not_publicly_cacheable(self):
        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("finanzas:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Cache-Control"], "private, no-store")

    def test_transfer_form_blocks_self_transfer(self):
        form = TransferenciaForm(
            data={
                "receptor_username": "alice",
                "monto": "20.00",
                "concepto": "self transfer",
            },
            emisor=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("receptor_username", form.errors)

    def test_db_constraint_blocks_self_transfer(self):
        with self.assertRaises(IntegrityError):
            Transferencia.objects.create(
                emisor=self.user,
                receptor=self.user,
                monto=10,
                concepto="invalid",
            )

    def test_db_constraint_blocks_non_positive_transfer_amount(self):
        with self.assertRaises(IntegrityError):
            Transferencia.objects.create(
                emisor=self.user,
                receptor=self.other_user,
                monto=0,
                concepto="invalid amount",
            )

    def test_health_ready_endpoint_does_not_expose_db_details(self):
        response = self.client.get("/health/ready/")
        self.assertIn(response.status_code, (200, 503))
        payload = response.json()
        self.assertEqual(set(payload.keys()), {"status"})

    def test_api_v1_dashboard_summary_requires_authentication(self):
        response = self.client.get("/api/v1/dashboard/summary")
        self.assertIn(response.status_code, (401, 403))

    def test_api_v1_dashboard_summary_returns_payload(self):
        self.client.login(username="alice", password="password123")
        response = self.client.get("/api/v1/dashboard/summary")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("ingresos_totales", payload)
        self.assertIn("gastos_totales", payload)
        self.assertIn("balance", payload)

class TransaccionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")
        
        self.categoria_ingreso, _ = Categoria.objects.get_or_create(
            usuario=self.user,
            nombre="Salario",
            defaults={"tipo": "ingreso"}
        )
        self.categoria_gasto, _ = Categoria.objects.get_or_create(
            usuario=self.user,
            nombre="Comida",
            defaults={"tipo": "gasto"}
        )

    def test_lista_transacciones(self):
        # Crear transacciones de prueba
        Transaccion.objects.create(
            usuario=self.user,
            monto=1000,
            tipo="ingreso",
            categoria=self.categoria_ingreso,
            descripcion="Ingreso prueba"
        )
        Transaccion.objects.create(
            usuario=self.user,
            monto=50,
            tipo="gasto",
            categoria=self.categoria_gasto,
            descripcion="Gasto prueba"
        )
        
        response = self.client.get(reverse("finanzas:lista_transacciones"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ingreso prueba")
        self.assertContains(response, "Gasto prueba")
        self.assertEqual(len(response.context["transacciones"]), 2)

    def test_agregar_ingreso(self):
        url = reverse("finanzas:nueva_transaccion")
        data = {
            "monto": "2000.00",
            "tipo": "ingreso",
            "categoria": self.categoria_ingreso.id,
            "descripcion": "Nuevo ingreso",
            "fecha": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        }
        
        response = self.client.post(url, data)
        # Debería redirigir a la lista de transacciones
        self.assertRedirects(response, reverse("finanzas:lista_transacciones"))
        
        # Verificar que se creó
        self.assertTrue(Transaccion.objects.filter(descripcion="Nuevo ingreso", monto=2000).exists())

    def test_agregar_gasto(self):
        url = reverse("finanzas:nueva_transaccion")
        data = {
            "monto": "150.50",
            "tipo": "gasto",
            "categoria": self.categoria_gasto.id,
            "descripcion": "Nuevo gasto",
            "fecha": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        }
        
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("finanzas:lista_transacciones"))
        
        self.assertTrue(Transaccion.objects.filter(descripcion="Nuevo gasto", monto=150.50).exists())

    def test_agregar_transaccion_monto_invalido(self):
        url = reverse("finanzas:nueva_transaccion")
        # Monto negativo/cero debería fallar si hay validación en form/model
        # El modelo tiene check constraint monto__gt=0
        data = {
            "monto": "-50.00",
            "tipo": "gasto",
            "categoria": self.categoria_gasto.id,
            "descripcion": "Gasto invalido",
            "fecha": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        }
        
        response = self.client.post(url, data)
        # Si el form valida, debería volver a mostrar el formulario con errores (status 200), no redirigir
        self.assertEqual(response.status_code, 200) 
        self.assertFalse(Transaccion.objects.filter(descripcion="Gasto invalido").exists())
