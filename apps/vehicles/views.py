"""Views for vehicles app."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.audit.models import AuditLog

from .forms import ElectricVehicleDetailForm, UsedVehicleAssessmentForm, VehicleForm, VehicleStatusForm
from .models import ElectricVehicleDetail, UsedVehicleAssessment, Vehicle, VehicleStatus


class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_manager


class TechnicianRequiredMixin(UserPassesTestMixin):
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_technician


class CompanyFilterMixin:
    """Filter queryset to user's company unless administrator."""

    def get_queryset(self):
        qs = Vehicle.objects.select_related("company", "created_by")
        user = self.request.user
        if not user.is_administrator:
            qs = qs.filter(company=user.company)
        return qs


class VehicleListView(LoginRequiredMixin, CompanyFilterMixin, ListView):
    model = Vehicle
    template_name = "vehicles/vehicle_list.html"
    context_object_name = "vehicles"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get("q", "")
        status = self.request.GET.get("status", "")
        vehicle_type = self.request.GET.get("type", "")
        drive_type = self.request.GET.get("drive", "")

        if search:
            qs = qs.filter(
                Q(stock_number__icontains=search)
                | Q(manufacturer__icontains=search)
                | Q(model__icontains=search)
                | Q(serial_number__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        if vehicle_type:
            qs = qs.filter(vehicle_type=vehicle_type)
        if drive_type:
            qs = qs.filter(drive_type=drive_type)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = VehicleStatus.choices
        ctx["vehicle_types"] = Vehicle._meta.get_field("vehicle_type").choices
        ctx["drive_types"] = Vehicle._meta.get_field("drive_type").choices
        ctx["search"] = self.request.GET.get("q", "")
        ctx["current_status"] = self.request.GET.get("status", "")
        return ctx


class VehicleDetailView(LoginRequiredMixin, CompanyFilterMixin, DetailView):
    model = Vehicle
    template_name = "vehicles/vehicle_detail.html"
    context_object_name = "vehicle"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["documents"] = self.object.documents.select_related("uploaded_by").order_by("-uploaded_at")
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(Vehicle)
        ctx["audit_logs"] = AuditLog.objects.filter(
            content_type=ct, object_id=str(self.object.pk)
        ).select_related("user").order_by("-timestamp")[:20]
        return ctx


class VehicleCreateView(LoginRequiredMixin, ManagerRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/vehicle_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        AuditLog.log(
            user=self.request.user,
            action=AuditLog.Action.CREATE,
            instance=self.object,
            description=f"Vehicle {self.object.stock_number} created",
        )
        messages.success(self.request, f"Vehicle {self.object.stock_number} created successfully.")
        return response

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if not user.is_administrator and user.company:
            form.fields["company"].queryset = form.fields["company"].queryset.filter(pk=user.company.pk)
        return form


class VehicleUpdateView(LoginRequiredMixin, ManagerRequiredMixin, CompanyFilterMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/vehicle_form.html"

    def form_valid(self, form):
        changed = list(form.changed_data)
        response = super().form_valid(form)
        AuditLog.log(
            user=self.request.user,
            action=AuditLog.Action.UPDATE,
            instance=self.object,
            description=f"Vehicle {self.object.stock_number} updated. Fields changed: {', '.join(changed)}",
        )
        messages.success(self.request, "Vehicle updated successfully.")
        return response


class VehicleStatusUpdateView(LoginRequiredMixin, TechnicianRequiredMixin, CompanyFilterMixin, UpdateView):
    """HTMX-friendly status change view."""

    model = Vehicle
    form_class = VehicleStatusForm
    template_name = "vehicles/partials/status_form.html"

    def form_valid(self, form):
        old_status = Vehicle.objects.get(pk=self.object.pk).status
        response = super().form_valid(form)
        AuditLog.log(
            user=self.request.user,
            action=AuditLog.Action.STATUS_CHANGE,
            instance=self.object,
            description=f"Status changed from {old_status} to {self.object.status}",
        )
        messages.success(self.request, f"Status updated to {self.object.get_status_display()}.")
        if self.request.htmx:
            return HttpResponse(
                f'<span class="badge bg-{self._status_colour(self.object.status)}">'
                f"{self.object.get_status_display()}</span>",
                status=200,
            )
        return response

    def _status_colour(self, status: str) -> str:
        colours = {
            VehicleStatus.ACQUIRED: "secondary",
            VehicleStatus.AWAITING_INSPECTION: "warning",
            VehicleStatus.PDI_IN_PROGRESS: "info",
            VehicleStatus.PREPARATION_REQUIRED: "warning",
            VehicleStatus.READY_FOR_SALE: "success",
            VehicleStatus.RESERVED: "primary",
            VehicleStatus.SOLD: "dark",
            VehicleStatus.ARCHIVED: "light",
        }
        return colours.get(status, "secondary")


class ElectricDetailUpdateView(LoginRequiredMixin, TechnicianRequiredMixin, UpdateView):
    """Update electric vehicle details."""

    model = ElectricVehicleDetail
    template_name = "vehicles/electric_detail_form.html"
    form_class = ElectricVehicleDetailForm

    def get_object(self, queryset=None):
        vehicle = get_object_or_404(Vehicle, pk=self.kwargs["pk"])
        obj, _ = ElectricVehicleDetail.objects.get_or_create(vehicle=vehicle)
        return obj

    def get_success_url(self):
        return reverse_lazy("vehicles:vehicle_detail", kwargs={"pk": self.kwargs["pk"]})


class UsedAssessmentUpdateView(LoginRequiredMixin, TechnicianRequiredMixin, UpdateView):
    """Update used vehicle assessment."""

    model = UsedVehicleAssessment
    template_name = "vehicles/used_assessment_form.html"
    form_class = UsedVehicleAssessmentForm

    def get_object(self, queryset=None):
        vehicle = get_object_or_404(Vehicle, pk=self.kwargs["pk"])
        obj, _ = UsedVehicleAssessment.objects.get_or_create(
            vehicle=vehicle, defaults={"assessed_by": self.request.user}
        )
        return obj

    def get_success_url(self):
        return reverse_lazy("vehicles:vehicle_detail", kwargs={"pk": self.kwargs["pk"]})
