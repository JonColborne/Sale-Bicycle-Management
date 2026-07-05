"""REST API for reports app."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Count, Sum

from apps.vehicles.models import Vehicle, VehicleStatus, DriveType


class ReportViewSet(viewsets.ViewSet):
    """Reporting endpoints."""

    permission_classes = [IsAuthenticated]

    def get_base_queryset(self, request):
        qs = Vehicle.objects.all()
        if not request.user.is_administrator and request.user.company:
            qs = qs.filter(company=request.user.company)
        return qs

    def list(self, request):
        return Response(
            {
                "reports": [
                    {"name": "inventory", "url": "/api/v1/reports/inventory/"},
                    {"name": "pdi_status", "url": "/api/v1/reports/pdi_status/"},
                    {"name": "valuation", "url": "/api/v1/reports/valuation/"},
                    {"name": "margin", "url": "/api/v1/reports/margin/"},
                    {"name": "ebike", "url": "/api/v1/reports/ebike/"},
                ]
            }
        )

    @action(detail=False, methods=["get"])
    def inventory(self, request):
        qs = self.get_base_queryset(request)
        data = qs.values("vehicle_type", "status", "drive_type").annotate(count=Count("id"))
        return Response(list(data))

    @action(detail=False, methods=["get"])
    def valuation(self, request):
        qs = self.get_base_queryset(request)
        return Response(
            qs.aggregate(
                total_purchase=Sum("purchase_cost"),
                total_rrp=Sum("recommended_retail_price"),
                count=Count("id"),
            )
        )

    @action(detail=False, methods=["get"])
    def margin(self, request):
        qs = self.get_base_queryset(request).filter(status=VehicleStatus.SOLD)
        stats = qs.aggregate(
            total_sales=Sum("actual_sale_price"),
            total_cost=Sum("purchase_cost"),
            count=Count("id"),
        )
        total_sales = stats["total_sales"] or 0
        total_cost = stats["total_cost"] or 0
        stats["total_margin"] = total_sales - total_cost
        return Response(stats)

    @action(detail=False, methods=["get"])
    def ebike(self, request):
        qs = self.get_base_queryset(request).filter(drive_type=DriveType.ELECTRICALLY_ASSISTED)
        return Response(
            {
                "total": qs.count(),
                "by_status": list(qs.values("status").annotate(count=Count("id"))),
            }
        )
