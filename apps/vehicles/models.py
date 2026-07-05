"""Vehicle (stock) models."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class VehicleType(models.TextChoices):
    CHILDS_BIKE = "childs_bike", _("Child's Bike")
    BMX = "bmx", _("BMX")
    HYBRID = "hybrid", _("Hybrid")
    ROAD_BIKE = "road_bike", _("Road Bike")
    GRAVEL_BIKE = "gravel_bike", _("Gravel Bike")
    MTB_HARDTAIL = "mtb_hardtail", _("Mountain Bike - Hardtail")
    MTB_FULL_SUSPENSION = "mtb_full_suspension", _("Mountain Bike - Full Suspension")
    TRICYCLE = "tricycle", _("Tricycle")
    ADAPTIVE_LIGHT_VEHICLE = "adaptive_light_vehicle", _("Adaptive Light Vehicle")


class DriveType(models.TextChoices):
    CONVENTIONAL = "conventional", _("Conventional")
    ELECTRICALLY_ASSISTED = "electrically_assisted", _("Electrically Assisted")


class VehicleStatus(models.TextChoices):
    ACQUIRED = "acquired", _("Acquired")
    AWAITING_INSPECTION = "awaiting_inspection", _("Awaiting Inspection")
    PDI_IN_PROGRESS = "pdi_in_progress", _("PDI In Progress")
    PREPARATION_REQUIRED = "preparation_required", _("Preparation Required")
    READY_FOR_SALE = "ready_for_sale", _("Ready For Sale")
    RESERVED = "reserved", _("Reserved")
    SOLD = "sold", _("Sold")
    ARCHIVED = "archived", _("Archived")


class VehicleCondition(models.TextChoices):
    NEW = "new", _("New")
    USED = "used", _("Used")
    EX_DEMO = "ex_demo", _("Ex-Demo")
    TEST_BIKE = "test_bike", _("Test Bike")


class FrameMaterial(models.TextChoices):
    ALUMINIUM = "aluminium", _("Aluminium")
    CARBON = "carbon", _("Carbon")
    STEEL = "steel", _("Steel")
    TITANIUM = "titanium", _("Titanium")
    CHROMOLY = "chromoly", _("Chromoly")
    OTHER = "other", _("Other")


class Vehicle(models.Model):
    """Represents a bicycle or adaptive vehicle in stock."""

    # Identification
    stock_number = models.CharField(max_length=20, unique=True, editable=False)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.PROTECT,
        related_name="vehicles",
    )

    # Classification
    vehicle_type = models.CharField(max_length=30, choices=VehicleType.choices)
    drive_type = models.CharField(max_length=30, choices=DriveType.choices, default=DriveType.CONVENTIONAL)
    condition = models.CharField(max_length=20, choices=VehicleCondition.choices, default=VehicleCondition.NEW)
    status = models.CharField(max_length=30, choices=VehicleStatus.choices, default=VehicleStatus.ACQUIRED)

    # Vehicle details
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=200)
    model_year = models.PositiveSmallIntegerField(null=True, blank=True)
    colour = models.CharField(max_length=100, blank=True)
    frame_size = models.CharField(max_length=50, blank=True)
    frame_material = models.CharField(max_length=20, choices=FrameMaterial.choices, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)

    # Purchase information
    supplier = models.CharField(max_length=200, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    # Pricing
    recommended_retail_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    minimum_sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    actual_sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    # Notes
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicles_created",
    )

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["stock_number"]),
            models.Index(fields=["serial_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.stock_number} - {self.manufacturer} {self.model}"

    def get_absolute_url(self) -> str:
        return reverse("vehicles:vehicle_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs) -> None:
        if not self.stock_number:
            self.stock_number = self._generate_stock_number()
        super().save(*args, **kwargs)

    def _generate_stock_number(self) -> str:
        """Generate a stock number in the format PREFIX-YYYY-NNNN."""
        from django.utils import timezone

        year = timezone.now().year
        prefix = self.company.slug.upper()
        last = (
            Vehicle.objects.filter(company=self.company, stock_number__startswith=f"{prefix}-{year}-")
            .order_by("stock_number")
            .last()
        )
        if last:
            last_seq = int(last.stock_number.split("-")[-1])
            seq = last_seq + 1
        else:
            seq = 1
        return f"{prefix}-{year}-{seq:04d}"

    @property
    def margin(self):
        """Calculate margin between purchase cost and sale price."""
        if self.actual_sale_price and self.purchase_cost:
            return self.actual_sale_price - self.purchase_cost
        return None

    @property
    def is_electric(self) -> bool:
        return self.drive_type == DriveType.ELECTRICALLY_ASSISTED


class ElectricVehicleDetail(models.Model):
    """Additional details for electrically assisted vehicles."""

    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="electric_detail")
    motor_manufacturer = models.CharField(max_length=100, blank=True)
    motor_serial_number = models.CharField(max_length=100, blank=True)
    battery_serial_number = models.CharField(max_length=100, blank=True)
    charger_serial_number = models.CharField(max_length=100, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    diagnostic_notes = models.TextField(blank=True)
    battery_health_percentage = models.PositiveSmallIntegerField(null=True, blank=True)
    last_diagnostic_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _("Electric Vehicle Detail")
        verbose_name_plural = _("Electric Vehicle Details")

    def __str__(self) -> str:
        return f"Electric detail for {self.vehicle.stock_number}"


class UsedVehicleAssessment(models.Model):
    """Assessment record for used/ex-demo vehicles."""

    class ConditionRating(models.TextChoices):
        EXCELLENT = "excellent", _("Excellent")
        GOOD = "good", _("Good")
        FAIR = "fair", _("Fair")
        POOR = "poor", _("Poor")

    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="used_assessment")
    assessed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="assessments_performed",
    )
    assessment_date = models.DateField(auto_now_add=True)

    frame_condition = models.CharField(max_length=20, choices=ConditionRating.choices, blank=True)
    fork_condition = models.CharField(max_length=20, choices=ConditionRating.choices, blank=True)
    drivetrain_condition = models.CharField(max_length=20, choices=ConditionRating.choices, blank=True)
    wheels_condition = models.CharField(max_length=20, choices=ConditionRating.choices, blank=True)
    brakes_condition = models.CharField(max_length=20, choices=ConditionRating.choices, blank=True)
    suspension_condition = models.CharField(max_length=20, choices=ConditionRating.choices, blank=True)
    electrical_condition = models.CharField(max_length=20, choices=ConditionRating.choices, blank=True)

    estimated_repair_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_repair_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preparation_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Used Vehicle Assessment")
        verbose_name_plural = _("Used Vehicle Assessments")

    def __str__(self) -> str:
        return f"Assessment for {self.vehicle.stock_number}"
