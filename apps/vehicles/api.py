"""REST API views for vehicles app."""

from rest_framework import filters, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ElectricVehicleDetail, Vehicle


class ElectricDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectricVehicleDetail
        fields = "__all__"


class VehicleSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    vehicle_type_display = serializers.CharField(source="get_vehicle_type_display", read_only=True)
    drive_type_display = serializers.CharField(source="get_drive_type_display", read_only=True)
    condition_display = serializers.CharField(source="get_condition_display", read_only=True)
    margin = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    electric_detail = ElectricDetailSerializer(read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "stock_number",
            "company",
            "vehicle_type",
            "vehicle_type_display",
            "drive_type",
            "drive_type_display",
            "condition",
            "condition_display",
            "status",
            "status_display",
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
            "margin",
            "notes",
            "created_at",
            "updated_at",
            "electric_detail",
        ]
        read_only_fields = ["id", "stock_number", "created_at", "updated_at"]


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["stock_number", "manufacturer", "model", "serial_number"]
    ordering_fields = ["stock_number", "manufacturer", "status", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Vehicle.objects.select_related("company", "electric_detail")
        user = self.request.user
        if not user.is_administrator:
            qs = qs.filter(company=user.company)
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        qs = self.get_queryset()
        from django.db.models import Count, Sum
        stats = qs.aggregate(
            total=Count("id"),
            total_purchase_cost=Sum("purchase_cost"),
            total_rrp=Sum("recommended_retail_price"),
        )
        by_status = dict(qs.values_list("status").annotate(count=Count("id")))
        return Response({"summary": stats, "by_status": by_status})
