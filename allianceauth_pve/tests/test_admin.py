from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory
from django.utils import timezone

from allianceauth.tests.auth_utils import AuthUtils

from ..models import Rotation, Entry, EntryCharacter, EntryRole
from ..admin import EntryCharacterInline, RotationAdmin


class TestEntryCharacterAdmin(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)
        cls.testuser.is_superuser = True
        cls.testuser.save()

        cls.rotation: Rotation = Rotation.objects.create(
            name='test1rot'
        )

        entry: Entry = Entry.objects.create(
            rotation=cls.rotation,
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

        cls.rotation.actual_total = 900_000_000
        cls.rotation.is_closed = True
        cls.rotation.closed_at = timezone.now()
        cls.rotation.save()

        cls.modeladmin = EntryCharacterInline(EntryCharacter, AdminSite())

        request_factory = RequestFactory()
        cls.request = request_factory.get('/fake')
        cls.request.user = cls.testuser

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

        self.assertAlmostEqual(self.modeladmin.estimated_share_total(row), 1_000_000_000.0, places=2)

    def test_actual_share_total(self):
        qs = self.modeladmin.get_queryset(request=self.request)

        self.assertEqual(qs.count(), 1)

        row = qs[0]

        self.assertAlmostEqual(self.modeladmin.actual_share_total(row), 900_000_000.0, places=2)
