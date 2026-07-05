"""Admin configuration for vehicles app."""

from django.contrib import admin

from .models import ElectricVehicleDetail, UsedVehicleAssessment, Vehicle


class ElectricVehicleDetailInline(admin.StackedInline):
    model = ElectricVehicleDetail
    extra = 0


class UsedVehicleAssessmentInline(admin.StackedInline):
    model = UsedVehicleAssessment
    extra = 0


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = [
        "stock_number",
        "manufacturer",
        "model",
        "vehicle_type",
        "drive_type",
        "condition",
        "status",
        "company",
        "purchase_cost",
        "recommended_retail_price",
    ]
    list_filter = ["company", "vehicle_type", "drive_type", "condition", "status"]
    search_fields = ["stock_number", "manufacturer", "model", "serial_number"]
    readonly_fields = ["stock_number", "created_at", "updated_at", "created_by"]
    inlines = [ElectricVehicleDetailInline, UsedVehicleAssessmentInline]

    fieldsets = (
        ("Identification", {"fields": ("stock_number", "company", "serial_number")}),
        ("Classification", {"fields": ("vehicle_type", "drive_type", "condition", "status")}),
        ("Vehicle Details", {"fields": ("manufacturer", "model", "model_year", "colour", "frame_size", "frame_material")}),
        ("Purchase", {"fields": ("supplier", "purchase_date", "purchase_cost")}),
        ("Pricing", {"fields": ("recommended_retail_price", "minimum_sale_price", "actual_sale_price")}),
        ("Notes", {"fields": ("notes",)}),
        ("Metadata", {"fields": ("created_at", "updated_at", "created_by"), "classes": ("collapse",)}),
    )
