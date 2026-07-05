"""Admin configuration for documents app."""

from django.contrib import admin

from .models import VehicleDocument


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "vehicle", "category", "uploaded_by", "uploaded_at"]
    list_filter = ["category", "vehicle__company"]
    search_fields = ["title", "vehicle__stock_number"]
    readonly_fields = ["uploaded_at", "updated_at", "uploaded_by"]
