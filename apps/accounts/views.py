"""Views for accounts app."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ProfileUpdateForm, UserRegistrationForm, UserUpdateForm
from .models import User


class AdministratorRequiredMixin(UserPassesTestMixin):
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_administrator


class UserListView(LoginRequiredMixin, AdministratorRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 25

    def get_queryset(self):
        return User.objects.select_related("company").order_by("last_name", "first_name")


class UserCreateView(LoginRequiredMixin, AdministratorRequiredMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        messages.success(self.request, "User created successfully.")
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, AdministratorRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        messages.success(self.request, "User updated successfully.")
        return super().form_valid(form)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/user_detail.html"
    context_object_name = "profile_user"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = "accounts/profile_form.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)
