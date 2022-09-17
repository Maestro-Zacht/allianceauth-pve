import datetime

from django.test import TestCase
from django.utils import timezone

from allianceauth.tests.auth_utils import AuthUtils

from ..models import Rotation, Entry, EntryCharacter, EntryRole
from ..actions import running_averages


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
            estimated_total=1_000_000_000.0
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

        entry.update_share_totals()

        rotation.actual_total = 900_000_000
        rotation.is_closed = True
        rotation.closed_at = timezone.now()
        rotation.save()
        for e in rotation.entries.all():
            e.update_share_totals()

    def test_valid_interval(self):
        res = running_averages(self.testuser, timezone.now() - datetime.timedelta(days=1), timezone.now() + datetime.timedelta(days=1))

        self.assertEqual(res['estimated_total'], 1_000_000_000)
        self.assertEqual(res['actual_total'], 900_000_000)
        self.assertEqual(res['helped_setups'], 0)

    def test_empty_interval(self):
        res = running_averages(self.testuser, timezone.now() - datetime.timedelta(days=2), timezone.now() - datetime.timedelta(days=1))

        self.assertDictEqual(res, {})
