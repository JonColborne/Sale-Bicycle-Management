"""Company models."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    """Represents an organisation (e.g., The Bike Inn, Helmwind Cycles)."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=20, unique=True, help_text="Short code used in stock numbers (e.g. TBI, HWC)")
    address_line_1 = models.CharField(max_length=200, blank=True)
    address_line_2 = models.CharField(max_length=200, blank=True)
    town = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
