"""Tests for the vehicles app."""

from decimal import Decimal

from django.test import TestCase

from apps.companies.models import Company
from apps.vehicles.models import (
    DriveType,
    Vehicle,
    VehicleCondition,
    VehicleStatus,
    VehicleType,
)


class VehicleModelTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="The Bike Inn", slug="TBI")

    def test_stock_number_auto_generated(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.HYBRID,
            drive_type=DriveType.CONVENTIONAL,
            condition=VehicleCondition.NEW,
            manufacturer="Trek",
            model="FX 3",
        )
        self.assertRegex(vehicle.stock_number, r"^TBI-\d{4}-\d{4}$")

    def test_stock_number_sequential(self):
        v1 = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.HYBRID,
            manufacturer="Trek",
            model="FX 3",
        )
        v2 = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.HYBRID,
            manufacturer="Trek",
            model="FX 4",
        )
        seq1 = int(v1.stock_number.split("-")[-1])
        seq2 = int(v2.stock_number.split("-")[-1])
        self.assertEqual(seq2, seq1 + 1)

    def test_vehicle_str(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.ROAD_BIKE,
            manufacturer="Giant",
            model="Defy",
        )
        self.assertIn("Giant", str(vehicle))
        self.assertIn("Defy", str(vehicle))

    def test_vehicle_default_status(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.BMX,
            manufacturer="Haro",
            model="Downtown",
        )
        self.assertEqual(vehicle.status, VehicleStatus.ACQUIRED)

    def test_margin_calculation(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.MTB_HARDTAIL,
            manufacturer="Canyon",
            model="Grand Canyon",
            purchase_cost=Decimal("500.00"),
            actual_sale_price=Decimal("749.00"),
        )
        self.assertEqual(vehicle.margin, Decimal("249.00"))

    def test_margin_none_when_no_sale_price(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.HYBRID,
            manufacturer="Trek",
            model="FX 2",
            purchase_cost=Decimal("400.00"),
        )
        self.assertIsNone(vehicle.margin)

    def test_is_electric_false_for_conventional(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.ROAD_BIKE,
            drive_type=DriveType.CONVENTIONAL,
            manufacturer="Specialized",
            model="Allez",
        )
        self.assertFalse(vehicle.is_electric)

    def test_is_electric_true_for_electrically_assisted(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.HYBRID,
            drive_type=DriveType.ELECTRICALLY_ASSISTED,
            manufacturer="Ribble",
            model="Hybrid AL e",
        )
        self.assertTrue(vehicle.is_electric)

    def test_stock_number_different_companies(self):
        """Different companies get separate sequential numbers."""
        company2 = Company.objects.create(name="Helmwind Cycles", slug="HWC")
        v1 = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.HYBRID,
            manufacturer="Trek",
            model="FX",
        )
        v2 = Vehicle.objects.create(
            company=company2,
            vehicle_type=VehicleType.HYBRID,
            manufacturer="Trek",
            model="FX",
        )
        self.assertTrue(v1.stock_number.startswith("TBI-"))
        self.assertTrue(v2.stock_number.startswith("HWC-"))

    def test_absolute_url(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.HYBRID,
            manufacturer="Trek",
            model="FX",
        )
        url = vehicle.get_absolute_url()
        self.assertIn(str(vehicle.pk), url)
