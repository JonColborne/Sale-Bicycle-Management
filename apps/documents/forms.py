"""Forms for documents app."""

from django import forms

from .models import VehicleDocument


class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = ["category", "title", "file", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
