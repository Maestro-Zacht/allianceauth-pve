import datetime

from django.utils import timezone

from allianceauth_pve.models import Rotation, RotationPreset
from allianceauth_pve.utils import ensure_rotation_presets_applied, running_averages

from .utils import PveTestBase


class TestRunningAverages(PveTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser, cls.testcharacter = cls.make_user(
            "aauth_testuser", 2116790529, "aauth_testchar"
        )

        rotation = cls.make_rotation(name="test1rot")

        cls.make_entry(rotation, cls.testuser, cls.testcharacter)

        rotation.actual_total = 900_000_000
        rotation.is_closed = True
        rotation.closed_at = timezone.now()
        rotation.save()

    def test_valid_interval(self):
        res = running_averages(
            self.testuser,
            timezone.now() - datetime.timedelta(days=1),
            timezone.now() + datetime.timedelta(days=1),
        )

        self.assertEqual(res["estimated_total"], 1_000_000_000)
        self.assertEqual(res["actual_total"], 900_000_000)
        self.assertEqual(res["helped_setups"], 0)

    def test_empty_interval(self):
        res = running_averages(
            self.testuser,
            timezone.now() - datetime.timedelta(days=2),
            timezone.now() - datetime.timedelta(days=1),
        )

        self.assertDictEqual(
            res, {"helped_setups": 0, "estimated_total": 0.0, "actual_total": 0.0}
        )


class TestEnsureRotationPresetsApplied(PveTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser, cls.testcharacter = cls.make_user(
            "aauth_testuser", 2116790529, "aauth_testchar"
        )

        cls.rotation = cls.make_rotation(name="test1rot")

        cls.preset = RotationPreset.objects.create(
            name="test1rot",
        )

    def test_no_missing(self):
        ensure_rotation_presets_applied()

        self.assertEqual(Rotation.objects.count(), 1)

    def test_missing(self):
        self.rotation.delete()

        ensure_rotation_presets_applied()

        self.assertEqual(Rotation.objects.count(), 1)
        self.assertEqual(Rotation.objects.first().name, "test1rot")

    def test_ignore_closed(self):
        self.rotation.delete()
        self.make_rotation(name="test1rot", is_closed=True)

        ensure_rotation_presets_applied()

        self.assertEqual(Rotation.objects.count(), 2)
        self.assertEqual(Rotation.objects.filter(is_closed=False).count(), 1)
        self.assertEqual(
            Rotation.objects.filter(is_closed=False).first().name, "test1rot"
        )

    def test_new_preset(self):
        new_preset = RotationPreset.objects.create(
            name="test2rot",
        )

        ensure_rotation_presets_applied()

        self.assertEqual(Rotation.objects.count(), 2)
        self.assertEqual(Rotation.objects.filter(is_closed=False).count(), 2)
        self.assertCountEqual(
            Rotation.objects.filter(is_closed=False).values_list("name", flat=True),
            [self.preset.name, new_preset.name],
        )
