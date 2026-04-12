import datetime

from django.test import TestCase
from django.utils import timezone

from allianceauth.tests.auth_utils import AuthUtils

from ..models import Rotation, Entry, EntryCharacter, EntryRole, RotationPreset
from ..utils import running_averages, ensure_rotation_presets_applied


class TestRunningAverages(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        rotation: Rotation = Rotation.objects.create(
            name='test1rot'
        )

        entry: Entry = Entry.objects.create(
            rotation=rotation,
            created_by=cls.testuser,
            estimated_total=1_000_000_000
        )

        role = EntryRole.objects.create(
            entry=entry,
            name='testrole1',
            value=1
        )

        share = EntryCharacter.objects.create(
            entry=entry,
            user=cls.testuser,
            user_character=cls.testcharacter,
            role=role,
            site_count=1,
            helped_setup=False
        )

        rotation.actual_total = 900_000_000
        rotation.is_closed = True
        rotation.closed_at = timezone.now()
        rotation.save()

    def test_valid_interval(self):
        res = running_averages(self.testuser, timezone.now() - datetime.timedelta(days=1), timezone.now() + datetime.timedelta(days=1))

        self.assertEqual(res['estimated_total'], 1_000_000_000)
        self.assertEqual(res['actual_total'], 900_000_000)
        self.assertEqual(res['helped_setups'], 0)

    def test_empty_interval(self):
        res = running_averages(self.testuser, timezone.now() - datetime.timedelta(days=2), timezone.now() - datetime.timedelta(days=1))

        self.assertDictEqual(res, {'helped_setups': 0, 'estimated_total': 0.0, 'actual_total': 0.0})


class TestEnsureRotationPresetsApplied(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.rotation = Rotation.objects.create(
            name='test1rot'
        )

        cls.preset = RotationPreset.objects.create(
            name='test1rot',
        )

    def test_no_missing(self):
        ensure_rotation_presets_applied()

        self.assertEqual(Rotation.objects.count(), 1)

    def test_missing(self):
        self.rotation.delete()

        ensure_rotation_presets_applied()

        self.assertEqual(Rotation.objects.count(), 1)
        self.assertEqual(Rotation.objects.first().name, 'test1rot')

    def test_ignore_closed(self):
        self.rotation.delete()
        Rotation.objects.create(
            name='test1rot',
            is_closed=True
        )

        ensure_rotation_presets_applied()

        self.assertEqual(Rotation.objects.count(), 2)
        self.assertEqual(Rotation.objects.filter(is_closed=False).count(), 1)
        self.assertEqual(Rotation.objects.filter(is_closed=False).first().name, 'test1rot')

    def test_new_preset(self):
        new_preset = RotationPreset.objects.create(
            name='test2rot',
        )

        ensure_rotation_presets_applied()

        self.assertEqual(Rotation.objects.count(), 2)
        self.assertEqual(Rotation.objects.filter(is_closed=False).count(), 2)
        self.assertCountEqual(
            Rotation.objects.filter(is_closed=False).values_list('name', flat=True),
            [self.preset.name, new_preset.name]
        )
