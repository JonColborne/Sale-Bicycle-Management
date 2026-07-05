"""Tests for the PDI app."""

from django.test import TestCase

from apps.accounts.models import User, UserRole
from apps.companies.models import Company
from apps.pdi.models import (
    PDIInspection,
    PDIItemStatus,
    PDITemplate,
    PDITemplateItem,
    PDITemplateLayer,
)
from apps.pdi.services import build_inspection_for_vehicle
from apps.vehicles.models import DriveType, Vehicle, VehicleType


_PW = "testpass123!"


class PDIServiceTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="The Bike Inn", slug="TBI")
        self.technician = User.objects.create_user(
            **{"username": "tech", "email": "tech@example.com", "password": _PW, "role": UserRole.TECHNICIAN}
        )

        # Create a universal template
        self.universal = PDITemplate.objects.create(
            name="Universal PDI",
            layer=PDITemplateLayer.UNIVERSAL,
            is_active=True,
        )
        PDITemplateItem.objects.create(
            template=self.universal,
            section="Safety",
            description="Frame inspection",
            is_mandatory=True,
            order=1,
        )

        # Create vehicle-type specific template
        self.hybrid_template = PDITemplate.objects.create(
            name="Hybrid PDI",
            layer=PDITemplateLayer.VEHICLE_TYPE,
            vehicle_type=VehicleType.HYBRID,
            is_active=True,
        )
        PDITemplateItem.objects.create(
            template=self.hybrid_template,
            section="Hybrid Specific",
            description="Mudguard check",
            is_mandatory=True,
            order=1,
        )

        # Create electric template
        self.electric_template = PDITemplate.objects.create(
            name="Electric Vehicle PDI",
            layer=PDITemplateLayer.ELECTRIC,
            is_active=True,
        )
        PDITemplateItem.objects.create(
            template=self.electric_template,
            section="Electrical",
            description="Battery security",
            is_mandatory=True,
            order=1,
        )

    def test_build_inspection_universal_items(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.ROAD_BIKE,
            drive_type=DriveType.CONVENTIONAL,
            manufacturer="Giant",
            model="Defy",
        )
        inspection = build_inspection_for_vehicle(vehicle, self.technician)
        self.assertIsInstance(inspection, PDIInspection)
        # Universal items should be included
        self.assertEqual(inspection.items.count(), 1)

    def test_build_inspection_includes_type_specific(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.HYBRID,
            drive_type=DriveType.CONVENTIONAL,
            manufacturer="Trek",
            model="FX 3",
        )
        inspection = build_inspection_for_vehicle(vehicle, self.technician)
        # Universal (1 item) + Hybrid (1 item) = 2 items
        self.assertEqual(inspection.items.count(), 2)

    def test_build_inspection_includes_electric_layer(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.HYBRID,
            drive_type=DriveType.ELECTRICALLY_ASSISTED,
            manufacturer="Ribble",
            model="Hybrid AL e",
        )
        inspection = build_inspection_for_vehicle(vehicle, self.technician)
        # Universal (1) + Hybrid (1) + Electric (1) = 3 items
        self.assertEqual(inspection.items.count(), 3)

    def test_inspection_items_default_to_pending(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.ROAD_BIKE,
            drive_type=DriveType.CONVENTIONAL,
            manufacturer="Trek",
            model="Domane",
        )
        inspection = build_inspection_for_vehicle(vehicle, self.technician)
        for item in inspection.items.all():
            self.assertEqual(item.status, PDIItemStatus.PENDING)

    def test_build_inspection_templates_applied(self):
        vehicle = Vehicle.objects.create(
            company=self.company,
            vehicle_type=VehicleType.HYBRID,
            drive_type=DriveType.CONVENTIONAL,
            manufacturer="Trek",
            model="FX",
        )
        inspection = build_inspection_for_vehicle(vehicle, self.technician)
        applied = set(inspection.templates_applied.values_list("pk", flat=True))
        self.assertIn(self.universal.pk, applied)
        self.assertIn(self.hybrid_template.pk, applied)
        self.assertNotIn(self.electric_template.pk, applied)
