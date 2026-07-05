"""Document management models."""

import os

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def vehicle_document_upload_path(instance, filename: str) -> str:
    """Upload path: documents/<company_slug>/<stock_number>/<filename>"""
    return f"documents/{instance.vehicle.company.slug}/{instance.vehicle.stock_number}/{filename}"


ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "heic", "docx", "xlsx"}


def validate_document_extension(value):
    ext = os.path.splitext(value.name)[1].lstrip(".").lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File type '{ext}' is not supported. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )


class DocumentCategory(models.TextChoices):
    PURCHASE_INVOICE = "purchase_invoice", _("Purchase Invoice")
    SUPPLIER_DOCUMENTATION = "supplier_documentation", _("Supplier Documentation")
    PDI_RECORD = "pdi_record", _("PDI Record")
    WARRANTY_DOCUMENTATION = "warranty_documentation", _("Warranty Documentation")
    SERVICE_DOCUMENTATION = "service_documentation", _("Service Documentation")
    DIAGNOSTIC_REPORT = "diagnostic_report", _("Diagnostic Report")
    BATTERY_REPORT = "battery_report", _("Battery Report")
    PHOTOS = "photos", _("Photos")
    SALE_DOCUMENTATION = "sale_documentation", _("Sale Documentation")
    OTHER = "other", _("Other")


class VehicleDocument(models.Model):
    """A document or image attached to a vehicle record."""

    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    category = models.CharField(max_length=30, choices=DocumentCategory.choices, default=DocumentCategory.OTHER)
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to=vehicle_document_upload_path,
        validators=[validate_document_extension],
    )
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="documents_uploaded",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Vehicle Document")
        verbose_name_plural = _("Vehicle Documents")
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.vehicle.stock_number})"

    @property
    def file_extension(self) -> str:
        return os.path.splitext(self.file.name)[1].lstrip(".").lower()

    @property
    def is_image(self) -> bool:
        return self.file_extension in {"jpg", "jpeg", "png", "heic"}
