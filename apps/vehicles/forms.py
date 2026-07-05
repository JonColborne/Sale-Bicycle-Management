"""Forms for vehicles app."""

from django import forms

from .models import ElectricVehicleDetail, UsedVehicleAssessment, Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "company",
            "vehicle_type",
            "drive_type",
            "condition",
            "status",
            "manufacturer",
            "model",
            "model_year",
            "colour",
            "frame_size",
            "frame_material",
            "serial_number",
            "supplier",
            "purchase_date",
            "purchase_cost",
            "recommended_retail_price",
            "minimum_sale_price",
            "actual_sale_price",
            "notes",
        ]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class ElectricVehicleDetailForm(forms.ModelForm):
    class Meta:
        model = ElectricVehicleDetail
        fields = [
            "motor_manufacturer",
            "motor_serial_number",
            "battery_serial_number",
            "charger_serial_number",
            "firmware_version",
            "battery_health_percentage",
            "last_diagnostic_date",
            "diagnostic_notes",
        ]
        widgets = {
            "last_diagnostic_date": forms.DateInput(attrs={"type": "date"}),
            "diagnostic_notes": forms.Textarea(attrs={"rows": 4}),
        }


class UsedVehicleAssessmentForm(forms.ModelForm):
    class Meta:
        model = UsedVehicleAssessment
        fields = [
            "frame_condition",
            "fork_condition",
            "drivetrain_condition",
            "wheels_condition",
            "brakes_condition",
            "suspension_condition",
            "electrical_condition",
            "estimated_repair_cost",
            "actual_repair_cost",
            "preparation_cost",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class VehicleStatusForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["status"]
