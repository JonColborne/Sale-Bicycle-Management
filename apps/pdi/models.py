"""PDI (Pre-Delivery Inspection) models."""

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.vehicles.models import DriveType, VehicleType


class PDITemplateLayer(models.TextChoices):
    UNIVERSAL = "universal", _("Universal (All Vehicles)")
    VEHICLE_TYPE = "vehicle_type", _("Vehicle Type Specific")
    ELECTRIC = "electric", _("Electric Vehicle")
    MANUFACTURER = "manufacturer", _("Manufacturer Specific")


class PDIItemStatus(models.TextChoices):
    PASS = "pass", _("Pass")
    FAIL = "fail", _("Fail")
    NA = "na", _("N/A")
    PENDING = "pending", _("Pending")


class PDITemplate(models.Model):
    """A reusable PDI template defining which inspection items to use."""

    name = models.CharField(max_length=200)
    layer = models.CharField(max_length=20, choices=PDITemplateLayer.choices)
    vehicle_type = models.CharField(
        max_length=30, choices=VehicleType.choices, blank=True, help_text="Leave blank for universal templates"
    )
    drive_type = models.CharField(
        max_length=30, choices=DriveType.choices, blank=True, help_text="Leave blank for non-drive-specific templates"
    )
    motor_manufacturer = models.CharField(
        max_length=100, blank=True, help_text="e.g. Bosch, Shimano Steps, Mahle"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("PDI Template")
        verbose_name_plural = _("PDI Templates")
        ordering = ["layer", "name"]

    def __str__(self) -> str:
        return self.name


class PDITemplateItem(models.Model):
    """A single check item within a PDI template."""

    template = models.ForeignKey(PDITemplate, on_delete=models.CASCADE, related_name="items")
    section = models.CharField(max_length=100, help_text="e.g. Safety, Assembly, Functional")
    description = models.CharField(max_length=500)
    guidance = models.TextField(blank=True, help_text="Technician guidance notes")
    is_mandatory = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _("PDI Template Item")
        verbose_name_plural = _("PDI Template Items")
        ordering = ["section", "order", "description"]

    def __str__(self) -> str:
        return f"{self.section}: {self.description}"


class PDIInspection(models.Model):
    """A PDI inspection record for a specific vehicle."""

    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.PROTECT,
        related_name="pdi_inspections",
    )
    templates_applied = models.ManyToManyField(
        PDITemplate,
        blank=True,
        related_name="inspections",
    )
    technician = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="pdi_inspections",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_complete = models.BooleanField(default=False)
    overall_result = models.CharField(
        max_length=10,
        choices=[("pass", "Pass"), ("fail", "Fail")],
        blank=True,
    )

    class Meta:
        verbose_name = _("PDI Inspection")
        verbose_name_plural = _("PDI Inspections")
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"PDI for {self.vehicle.stock_number} by {self.technician}"

    def get_absolute_url(self) -> str:
        return reverse("pdi:inspection_detail", kwargs={"pk": self.pk})


class PDIInspectionItem(models.Model):
    """A single completed check within a PDI inspection."""

    inspection = models.ForeignKey(PDIInspection, on_delete=models.CASCADE, related_name="items")
    template_item = models.ForeignKey(PDITemplateItem, on_delete=models.PROTECT, related_name="inspection_items")
    status = models.CharField(max_length=10, choices=PDIItemStatus.choices, default=PDIItemStatus.PENDING)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("PDI Inspection Item")
        verbose_name_plural = _("PDI Inspection Items")
        ordering = ["template_item__section", "template_item__order"]

    def __str__(self) -> str:
        return f"{self.template_item.description}: {self.status}"


class PDISignOff(models.Model):
    """Digital sign-off record for a completed PDI inspection."""

    inspection = models.OneToOneField(PDIInspection, on_delete=models.CASCADE, related_name="sign_off")
    technician = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="pdi_sign_offs",
    )
    signed_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=10, choices=[("pass", "Pass"), ("fail", "Fail")])
    signature_name = models.CharField(max_length=200, help_text="Technician's printed name")
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pdi_approvals",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("PDI Sign-Off")
        verbose_name_plural = _("PDI Sign-Offs")

    def __str__(self) -> str:
        return f"Sign-off: {self.inspection} - {self.result.upper()}"
