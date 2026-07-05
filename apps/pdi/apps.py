"""App configuration for pdi."""

from django.apps import AppConfig


class PdiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pdi"
    verbose_name = "Pdi"
