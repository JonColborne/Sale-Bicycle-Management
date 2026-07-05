"""REST API views for companies app."""

from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "slug", "town", "email", "phone", "website", "is_active"]
        read_only_fields = ["id"]


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_administrator:
            return Company.objects.all()
        if user.company:
            return Company.objects.filter(pk=user.company.pk)
        return Company.objects.none()
