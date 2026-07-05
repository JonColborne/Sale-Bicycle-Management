"""Tests for the companies app."""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.companies.models import Company

User = get_user_model()


class CompanyModelTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="The Bike Inn",
            slug="TBI",
            town="Example Town",
            email="info@thebikeinn.example.com",
        )

    def test_company_str(self):
        self.assertEqual(str(self.company), "The Bike Inn")

    def test_company_slug_unique(self):
        from django.db import IntegrityError
        with self.assertRaises(Exception):
            Company.objects.create(name="Another Company", slug="TBI")

    def test_company_defaults(self):
        self.assertTrue(self.company.is_active)
