from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.utils import timezone

from allianceauth.tests.auth_utils import AuthUtils

from ..models import Rotation, Entry, EntryCharacter, EntryRole
from ..admin import RotationAdmin


class TestRotationAdmin(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.rotation: Rotation = Rotation.objects.create(
            name='test1rot'
        )

        entry: Entry = Entry.objects.create(
            rotation=cls.rotation,
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

        cls.rotation.actual_total = 900_000_000
        cls.rotation.is_closed = True
        cls.rotation.closed_at = timezone.now()
        cls.rotation.save()
        for e in cls.rotation.entries.all():
            e.update_share_totals()

    def test_save_model(self):
        modeladmin = RotationAdmin(Rotation, AdminSite())

        self.rotation.actual_total = 950_000_000
        modeladmin.save_model(obj=self.rotation, request=None, form=None, change=None)
