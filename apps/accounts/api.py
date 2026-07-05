"""REST API views for accounts app."""

from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "full_name", "role", "company", "is_active"]
        read_only_fields = ["id"]

    def get_full_name(self, obj) -> str:
        return obj.get_full_name()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_administrator:
            return User.objects.select_related("company").all()
        return User.objects.filter(company=user.company).select_related("company")
