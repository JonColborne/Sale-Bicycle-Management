"""Views for PDI app."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.audit.models import AuditLog
from apps.vehicles.models import Vehicle, VehicleStatus
from apps.vehicles.views import TechnicianRequiredMixin

from .models import PDIInspection, PDIInspectionItem, PDISignOff, PDITemplate, PDIItemStatus
from .services import build_inspection_for_vehicle


class PDITemplateListView(LoginRequiredMixin, ListView):
    model = PDITemplate
    template_name = "pdi/template_list.html"
    context_object_name = "templates"

    def get_queryset(self):
        return PDITemplate.objects.filter(is_active=True).prefetch_related("items")


class PDIInspectionListView(LoginRequiredMixin, ListView):
    model = PDIInspection
    template_name = "pdi/inspection_list.html"
    context_object_name = "inspections"
    paginate_by = 25

    def get_queryset(self):
        qs = PDIInspection.objects.select_related("vehicle", "technician", "vehicle__company")
        user = self.request.user
        if not user.is_administrator:
            qs = qs.filter(vehicle__company=user.company)
        return qs


class PDIInspectionDetailView(LoginRequiredMixin, DetailView):
    model = PDIInspection
    template_name = "pdi/inspection_detail.html"
    context_object_name = "inspection"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        items = self.object.items.select_related("template_item").order_by(
            "template_item__section", "template_item__order"
        )
        sections = {}
        for item in items:
            section = item.template_item.section
            sections.setdefault(section, []).append(item)
        ctx["sections"] = sections
        ctx["has_sign_off"] = hasattr(self.object, "sign_off")
        return ctx


class PDIStartView(LoginRequiredMixin, TechnicianRequiredMixin, View):
    """Start a PDI inspection for a vehicle."""

    def post(self, request, vehicle_pk):
        vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)
        inspection = build_inspection_for_vehicle(vehicle, request.user)
        vehicle.status = VehicleStatus.PDI_IN_PROGRESS
        vehicle.save()
        AuditLog.log(
            user=request.user,
            action=AuditLog.Action.PDI_STARTED,
            instance=vehicle,
            description=f"PDI started for {vehicle.stock_number}",
        )
        messages.success(request, f"PDI inspection started for {vehicle.stock_number}.")
        return redirect("pdi:inspection_detail", pk=inspection.pk)


class PDIItemUpdateView(LoginRequiredMixin, TechnicianRequiredMixin, UpdateView):
    """Update a single PDI item status."""

    model = PDIInspectionItem
    fields = ["status", "notes"]
    template_name = "pdi/inspection_item_form.html"

    def get_success_url(self):
        return reverse_lazy("pdi:inspection_detail", kwargs={"pk": self.object.inspection.pk})

    def form_valid(self, form):
        form.instance.completed_at = timezone.now()
        return super().form_valid(form)


class PDICompleteView(LoginRequiredMixin, TechnicianRequiredMixin, View):
    """Mark a PDI inspection as complete."""

    def post(self, request, pk):
        inspection = get_object_or_404(PDIInspection, pk=pk)
        items = inspection.items.all()
        has_fail = items.filter(status=PDIItemStatus.FAIL).exists()
        has_pending = items.filter(status=PDIItemStatus.PENDING).exists()
        if has_pending:
            messages.error(request, "All items must be completed before finishing the inspection.")
            return redirect("pdi:inspection_detail", pk=pk)
        inspection.is_complete = True
        inspection.completed_at = timezone.now()
        inspection.overall_result = "fail" if has_fail else "pass"
        inspection.save()
        AuditLog.log(
            user=request.user,
            action=AuditLog.Action.PDI_COMPLETED,
            instance=inspection.vehicle,
            description=f"PDI completed for {inspection.vehicle.stock_number}. Result: {inspection.overall_result.upper()}",
        )
        messages.success(request, f"PDI completed. Result: {inspection.overall_result.upper()}")
        return redirect("pdi:inspection_detail", pk=pk)


class PDISignOffView(LoginRequiredMixin, TechnicianRequiredMixin, CreateView):
    """Digital sign-off for a completed PDI."""

    model = PDISignOff
    fields = ["result", "signature_name", "notes"]
    template_name = "pdi/sign_off_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.inspection = get_object_or_404(PDIInspection, pk=kwargs["inspection_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["inspection"] = self.inspection
        return ctx

    def form_valid(self, form):
        form.instance.inspection = self.inspection
        form.instance.technician = self.request.user
        response = super().form_valid(form)
        if self.inspection.overall_result == "pass":
            self.inspection.vehicle.status = VehicleStatus.READY_FOR_SALE
            self.inspection.vehicle.save()
        AuditLog.log(
            user=self.request.user,
            action=AuditLog.Action.PDI_SIGNED_OFF,
            instance=self.inspection.vehicle,
            description=f"PDI signed off by {self.request.user.get_full_name()}. Result: {form.instance.result.upper()}",
        )
        messages.success(self.request, "PDI signed off successfully.")
        return response

    def get_success_url(self):
        return reverse_lazy("pdi:inspection_detail", kwargs={"pk": self.inspection.pk})
