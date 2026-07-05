"""Tests for the accounts app."""

from django.test import TestCase

from apps.accounts.models import User, UserRole
from apps.companies.models import Company

_PW = "testpass123!"


def make_user(**kwargs):
    kwargs.setdefault("username", "user")
    kwargs.setdefault("email", "user@example.com")
    pw = kwargs.pop("password", _PW)
    return User.objects.create_user(**{**{"password": pw}, **kwargs})


class UserModelTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="The Bike Inn", slug="TBI")

    def test_user_str(self):
        user = make_user(username="jdoe", email="jdoe@example.com", first_name="John", last_name="Doe")
        self.assertIn("John", str(user))
        self.assertIn("Doe", str(user))

    def test_user_default_role(self):
        user = make_user(username="testuser", email="test@example.com")
        self.assertEqual(user.role, UserRole.READ_ONLY)

    def test_administrator_permissions(self):
        admin = make_user(username="admin", email="admin@example.com", role=UserRole.ADMINISTRATOR)
        self.assertTrue(admin.is_administrator)
        self.assertTrue(admin.is_manager)
        self.assertTrue(admin.is_technician)
        self.assertTrue(admin.is_sales)

    def test_manager_permissions(self):
        manager = make_user(username="manager", email="manager@example.com", role=UserRole.MANAGER)
        self.assertFalse(manager.is_administrator)
        self.assertTrue(manager.is_manager)
        self.assertTrue(manager.is_technician)

    def test_technician_permissions(self):
        tech = make_user(username="tech", email="tech@example.com", role=UserRole.TECHNICIAN)
        self.assertFalse(tech.is_manager)
        self.assertTrue(tech.is_technician)
        self.assertFalse(tech.is_sales)

    def test_read_only_has_no_elevated_permissions(self):
        user = make_user(username="readonly", email="readonly@example.com", role=UserRole.READ_ONLY)
        self.assertFalse(user.is_administrator)
        self.assertFalse(user.is_manager)
        self.assertFalse(user.is_technician)
        self.assertFalse(user.is_sales)

    def test_email_is_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_full_name_with_both_names(self):
        user = User(first_name="Jane", last_name="Smith", email="jane@example.com")
        self.assertEqual(user.get_full_name(), "Jane Smith")

    def test_full_name_falls_back_to_email(self):
        user = User(email="noname@example.com")
        self.assertEqual(user.get_full_name(), "noname@example.com")
