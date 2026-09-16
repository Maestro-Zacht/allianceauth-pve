from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.utils import timezone

from allianceauth_pve.admin import (
    EntryCharacterInline,
    RotationAdmin,
    RotationPresetAdmin,
)
from allianceauth_pve.models import EntryCharacter, Rotation

from .utils import PveTestBase


class TestRotationAdmin(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.modeladmin = RotationAdmin(Rotation, AdminSite())

    @patch("allianceauth_pve.admin.ensure_rotation_presets_applied")
    @patch("allianceauth_pve.admin.admin.ModelAdmin.save_model")
    def test_save_model(
        self,
        mock_save_model,
        mock_ensure_rotation_presets_applied,
    ):
        mock_ensure_rotation_presets_applied.return_value = None
        mock_save_model.return_value = None

        self.modeladmin.save_model(None, None, None, None)

        mock_ensure_rotation_presets_applied.assert_called_once()
        mock_save_model.assert_called_once()

    @patch("allianceauth_pve.admin.ensure_rotation_presets_applied")
    @patch("allianceauth_pve.admin.admin.ModelAdmin.delete_queryset")
    def test_delete_queryset(
        self,
        mock_delete_queryset,
        mock_ensure_rotation_presets_applied,
    ):
        mock_ensure_rotation_presets_applied.return_value = None
        mock_delete_queryset.return_value = None

        self.modeladmin.delete_queryset(None, None)

        mock_ensure_rotation_presets_applied.assert_called_once()
        mock_delete_queryset.assert_called_once()

    @patch("allianceauth_pve.admin.ensure_rotation_presets_applied")
    @patch("allianceauth_pve.admin.admin.ModelAdmin.delete_model")
    def test_delete_model(
        self, mock_delete_model, mock_ensure_rotation_presets_applied
    ):
        mock_ensure_rotation_presets_applied.return_value = None
        mock_delete_model.return_value = None

        self.modeladmin.delete_model(None, None)

        mock_ensure_rotation_presets_applied.assert_called_once()
        mock_delete_model.assert_called_once()


class TestEntryCharacterAdmin(PveTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.modeladmin = EntryCharacterInline(EntryCharacter, AdminSite())

        request_factory = RequestFactory()
        cls.request = request_factory.get("/fake")
        cls.request.user = cls.testuser

    @classmethod
    def setUpTestData(cls):
        cls.testuser, cls.testcharacter = cls.make_superuser(
            "aauth_testuser", 2116790529, "aauth_testchar"
        )

        cls.rotation = cls.make_rotation(name="test1rot")

        cls.make_entry(cls.rotation, cls.testuser, cls.testcharacter)

        cls.rotation.actual_total = 900_000_000
        cls.rotation.is_closed = True
        cls.rotation.closed_at = timezone.now()
        cls.rotation.save()

    def test_get_queryset(self):
        qs = self.modeladmin.get_queryset(request=self.request)

        self.assertEqual(qs.count(), 1)

        row = qs[0]

        self.assertAlmostEqual(row.estimated_share_total, 1_000_000_000.0, places=2)
        self.assertAlmostEqual(row.actual_share_total, 900_000_000.0, places=2)

    def test_estimated_share_total(self):
        qs = self.modeladmin.get_queryset(request=self.request)

        self.assertEqual(qs.count(), 1)

        row = qs[0]

        self.assertAlmostEqual(
            self.modeladmin.estimated_share_total(row), 1_000_000_000.0, places=2
        )

    def test_actual_share_total(self):
        qs = self.modeladmin.get_queryset(request=self.request)

        self.assertEqual(qs.count(), 1)

        row = qs[0]

        self.assertAlmostEqual(
            self.modeladmin.actual_share_total(row), 900_000_000.0, places=2
        )


class TestRotationPresetAdmin(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.modeladmin = RotationPresetAdmin(Rotation, AdminSite())

    @patch("allianceauth_pve.admin.ensure_rotation_presets_applied")
    @patch("allianceauth_pve.admin.admin.ModelAdmin.save_model")
    def test_save_model(
        self,
        mock_save_model,
        mock_ensure_rotation_presets_applied,
    ):
        mock_ensure_rotation_presets_applied.return_value = None
        mock_save_model.return_value = None

        self.modeladmin.save_model(None, None, None, None)

        mock_ensure_rotation_presets_applied.assert_called_once()
        mock_save_model.assert_called_once()
