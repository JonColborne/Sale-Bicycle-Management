"""PDI service layer - builds inspections from templates."""

from apps.vehicles.models import DriveType, Vehicle

from .models import PDIInspection, PDIInspectionItem, PDITemplate, PDITemplateLayer


def build_inspection_for_vehicle(vehicle: Vehicle, technician) -> PDIInspection:
    """
    Build a PDI inspection for a vehicle by applying the layered template system.

    Layer 1: Universal templates (applied to all)
    Layer 2: Vehicle type specific templates
    Layer 3: Electric vehicle templates (if electrically assisted)
    Layer 4: Manufacturer specific templates (if electric and motor manufacturer known)
    """
    inspection = PDIInspection.objects.create(vehicle=vehicle, technician=technician)
    templates = []

    # Layer 1: Universal
    universal = PDITemplate.objects.filter(layer=PDITemplateLayer.UNIVERSAL, is_active=True)
    templates.extend(universal)

    # Layer 2: Vehicle type specific
    type_specific = PDITemplate.objects.filter(
        layer=PDITemplateLayer.VEHICLE_TYPE,
        vehicle_type=vehicle.vehicle_type,
        is_active=True,
    )
    templates.extend(type_specific)

    # Layer 3: Electric vehicle
    if vehicle.drive_type == DriveType.ELECTRICALLY_ASSISTED:
        electric = PDITemplate.objects.filter(
            layer=PDITemplateLayer.ELECTRIC,
            is_active=True,
        )
        templates.extend(electric)

        # Layer 4: Manufacturer specific
        if hasattr(vehicle, "electric_detail") and vehicle.electric_detail.motor_manufacturer:
            manufacturer_specific = PDITemplate.objects.filter(
                layer=PDITemplateLayer.MANUFACTURER,
                motor_manufacturer__iexact=vehicle.electric_detail.motor_manufacturer,
                is_active=True,
            )
            templates.extend(manufacturer_specific)

    if templates:
        inspection.templates_applied.set(templates)

    # Create inspection items from all template items
    items = []
    seen_items = set()
    for template in templates:
        for item in template.items.all():
            if item.pk not in seen_items:
                items.append(
                    PDIInspectionItem(
                        inspection=inspection,
                        template_item=item,
                    )
                )
                seen_items.add(item.pk)

    PDIInspectionItem.objects.bulk_create(items)
    return inspection
