"""Forms for accounts app."""

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "company", "role"]


class UserUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "job_title",
            "company",
            "role",
            "is_active",
        ]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "job_title"]
