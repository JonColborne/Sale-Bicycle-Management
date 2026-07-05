"""Audit trail models."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    """Immutable audit record for all significant system actions."""

    class Action(models.TextChoices):
        CREATE = "create", _("Created")
        UPDATE = "update", _("Updated")
        DELETE = "delete", _("Deleted")
        STATUS_CHANGE = "status_change", _("Status Changed")
        DOCUMENT_UPLOAD = "document_upload", _("Document Uploaded")
        DOCUMENT_DELETE = "document_delete", _("Document Deleted")
        PDI_STARTED = "pdi_started", _("PDI Started")
        PDI_COMPLETED = "pdi_completed", _("PDI Completed")
        PDI_SIGNED_OFF = "pdi_signed_off", _("PDI Signed Off")
        USER_LOGIN = "user_login", _("User Logged In")
        USER_LOGOUT = "user_logout", _("User Logged Out")

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=30, choices=Action.choices)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # Generic FK to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=50, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # Extra data
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")
        ordering = ["-timestamp"]
        # Prevent editing
        default_permissions = ("view",)

    def __str__(self) -> str:
        return f"{self.timestamp} - {self.user} - {self.action}"

    @classmethod
    def log(
        cls,
        user,
        action: str,
        description: str,
        instance=None,
        ip_address: str | None = None,
        extra_data: dict | None = None,
    ) -> "AuditLog":
        """Convenience method to create an audit log entry."""
        kwargs = {
            "user": user,
            "action": action,
            "description": description,
            "ip_address": ip_address,
            "extra_data": extra_data or {},
        }
        if instance is not None:
            kwargs["content_type"] = ContentType.objects.get_for_model(instance)
            kwargs["object_id"] = str(instance.pk)
        return cls.objects.create(**kwargs)
