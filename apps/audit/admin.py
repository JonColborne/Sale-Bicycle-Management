"""Admin configuration for audit app."""

from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "user", "action", "description", "content_type", "object_id"]
    list_filter = ["action", "content_type"]
    search_fields = ["description", "user__email"]
    readonly_fields = ["timestamp", "user", "action", "description", "content_type", "object_id", "ip_address", "extra_data"]
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
