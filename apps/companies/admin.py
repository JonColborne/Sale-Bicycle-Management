"""Admin configuration for companies app."""

from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "town", "email", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug", "email"]
    prepopulated_fields = {"slug": ("name",)}
