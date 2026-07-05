"""Forms for companies app."""

from django import forms

from .models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "name",
            "slug",
            "address_line_1",
            "address_line_2",
            "town",
            "county",
            "postcode",
            "phone",
            "email",
            "website",
            "is_active",
        ]
