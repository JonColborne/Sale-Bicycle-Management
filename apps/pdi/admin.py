"""Admin configuration for PDI app."""

from django.contrib import admin

from .models import PDIInspection, PDIInspectionItem, PDISignOff, PDITemplate, PDITemplateItem


class PDITemplateItemInline(admin.TabularInline):
    model = PDITemplateItem
    extra = 1


@admin.register(PDITemplate)
class PDITemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "layer", "vehicle_type", "drive_type", "motor_manufacturer", "is_active"]
    list_filter = ["layer", "vehicle_type", "drive_type", "is_active"]
    search_fields = ["name", "motor_manufacturer"]
    inlines = [PDITemplateItemInline]


class PDIInspectionItemInline(admin.TabularInline):
    model = PDIInspectionItem
    extra = 0
    readonly_fields = ["template_item"]


@admin.register(PDIInspection)
class PDIInspectionAdmin(admin.ModelAdmin):
    list_display = ["vehicle", "technician", "started_at", "is_complete", "overall_result"]
    list_filter = ["is_complete", "overall_result", "vehicle__company"]
    search_fields = ["vehicle__stock_number", "technician__email"]
    readonly_fields = ["started_at"]
    inlines = [PDIInspectionItemInline]


@admin.register(PDISignOff)
class PDISignOffAdmin(admin.ModelAdmin):
    list_display = ["inspection", "technician", "signed_at", "result", "approved_by"]
    readonly_fields = ["signed_at"]
    list_filter = ["result"]
