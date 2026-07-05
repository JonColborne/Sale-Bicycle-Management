"""User and authentication models."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    ADMINISTRATOR = "administrator", _("Administrator")
    MANAGER = "manager", _("Manager")
    TECHNICIAN = "technician", _("Technician")
    SALES = "sales", _("Sales User")
    READ_ONLY = "read_only", _("Read Only")


class User(AbstractUser):
    """Extended user model with role and company association."""

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.READ_ONLY,
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    phone = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.get_full_name()} ({self.email})"

    @property
    def is_administrator(self) -> bool:
        return self.role == UserRole.ADMINISTRATOR

    @property
    def is_manager(self) -> bool:
        return self.role in (UserRole.ADMINISTRATOR, UserRole.MANAGER)

    @property
    def is_technician(self) -> bool:
        return self.role in (UserRole.ADMINISTRATOR, UserRole.MANAGER, UserRole.TECHNICIAN)

    @property
    def is_sales(self) -> bool:
        return self.role in (UserRole.ADMINISTRATOR, UserRole.MANAGER, UserRole.SALES)

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email
