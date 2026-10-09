from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.utils import timezone

from allianceauth_pve.admin import (
    EntryCharacterInline,
    RotationAdmin,
    RotationPresetAdmin,
)
from allianceauth_pve.models import (
    EntryCharacter,
    RoleSetup,
    Rotation,
    RotationPreset,
)

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


class TestLockRolesSetupAdmin(PveTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser, _ = cls.make_superuser("admin_super", 90600001, "AdminSuper")
        cls.setup = RoleSetup.objects.create(name="setup1")
        cls.other_setup = RoleSetup.objects.create(name="setup2")
        cls.rotation = cls.make_rotation(name="adminrot")
        cls.preset = RotationPreset.objects.create(name="adminpreset")

    def setUp(self):
        self.request = RequestFactory().get("/fake")
        self.request.user = self.superuser
        self.admins = (
            (RotationAdmin(Rotation, AdminSite()), self.rotation),
            (RotationPresetAdmin(RotationPreset, AdminSite()), self.preset),
        )

    def form_data(self, modeladmin, obj, **overrides):
        form = modeladmin.get_form(self.request, obj)(instance=obj)
        data = {
            name: form[name].value() for name in form.fields if name != "roles_setups"
        }
        data = {key: value for key, value in data.items() if value is not None}
        data.update(overrides)
        return data

    def test_roles_setups_readonly_when_locked(self):
        for modeladmin, obj in self.admins:
            with self.subTest(admin=type(modeladmin).__name__):
                self.assertNotIn(
                    "roles_setups", modeladmin.get_readonly_fields(self.request, obj)
                )
                self.assertNotIn(
                    "roles_setups", modeladmin.get_readonly_fields(self.request)
                )

                obj.lock_roles_setup = True
                self.assertIn(
                    "roles_setups", modeladmin.get_readonly_fields(self.request, obj)
                )

        self.assertIn(
            "closed_at",
            self.admins[0][0].get_readonly_fields(self.request, self.rotation),
        )

    def test_form_requires_exactly_one_setup(self):
        cases = (
            ([], False),
            ([self.setup.pk], True),
            ([self.setup.pk, self.other_setup.pk], False),
        )
        for modeladmin, obj in self.admins:
            form_class = modeladmin.get_form(self.request, obj)
            for setups, valid in cases:
                with self.subTest(admin=type(modeladmin).__name__, setups=setups):
                    form = form_class(
                        data=self.form_data(
                            modeladmin,
                            obj,
                            lock_roles_setup=True,
                            roles_setups=setups,
                        ),
                        instance=obj,
                    )
                    self.assertEqual(form.is_valid(), valid, form.errors)
                    if not valid:
                        self.assertIn("lock_roles_setup", form.errors)

    def test_form_skips_lock_check_when_setups_invalid(self):
        invalid_pk = RoleSetup.objects.order_by("-pk").first().pk + 1
        for modeladmin, obj in self.admins:
            form_class = modeladmin.get_form(self.request, obj)
            with self.subTest(admin=type(modeladmin).__name__):
                form = form_class(
                    data=self.form_data(
                        modeladmin,
                        obj,
                        lock_roles_setup=True,
                        roles_setups=[invalid_pk],
                    ),
                    instance=obj,
                )
                self.assertFalse(form.is_valid())
                self.assertIn("roles_setups", form.errors)
                self.assertNotIn("lock_roles_setup", form.errors)

    def test_form_allows_any_setups_when_unlocked(self):
        cases = (
            [],
            [self.setup.pk],
            [self.setup.pk, self.other_setup.pk],
        )
        for modeladmin, obj in self.admins:
            form_class = modeladmin.get_form(self.request, obj)
            for setups in cases:
                with self.subTest(admin=type(modeladmin).__name__, setups=setups):
                    form = form_class(
                        data=self.form_data(
                            modeladmin,
                            obj,
                            lock_roles_setup=False,
                            roles_setups=setups,
                        ),
                        instance=obj,
                    )
                    self.assertTrue(form.is_valid(), form.errors)

    def test_form_uses_saved_setups_when_readonly(self):
        for modeladmin, obj in self.admins:
            obj.lock_roles_setup = True
            obj.save()
            form_class = modeladmin.get_form(self.request, obj)
            self.assertNotIn("roles_setups", form_class.base_fields)
            for setups, valid in (([], False), ([self.setup], True)):
                obj.roles_setups.set(setups)
                with self.subTest(admin=type(modeladmin).__name__, setups=setups):
                    form = form_class(
                        data=self.form_data(modeladmin, obj, lock_roles_setup=True),
                        instance=obj,
                    )
                    self.assertEqual(form.is_valid(), valid, form.errors)
