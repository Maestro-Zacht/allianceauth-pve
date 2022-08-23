from django.test import TestCase
from django.utils import timezone

from allianceauth.tests.auth_utils import AuthUtils

from ..models import Rotation, Entry, EntryCharacter, EntryRole, RoleSetup, PveButton


class TestRoleSetup(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.rolesetup = RoleSetup.objects.create(name='testrolesetup')

    def test_str(self):
        self.assertEqual(str(self.rolesetup), self.rolesetup.name)


class TestPveButton(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.pvebutton = PveButton.objects.create(
            text='testbutton',
            amount=1
        )

    def test_str(self):
        self.assertEqual(str(self.pvebutton), self.pvebutton.text)


class TestRotation(TestCase):

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

    def test_summary_open(self):
        summary = self.rotation.summary

        self.assertEqual(summary.count(), 1)

        row = summary.first()

        self.assertEqual(row['user'], self.testuser.pk)
        self.assertEqual(row['helped_setups'], 0)
        self.assertEqual(row['estimated_total'], 1_000_000_000)
        self.assertEqual(row['actual_total'], 0)

    def test_summary_closed(self):
        self.rotation.actual_total = 900_000_000
        self.rotation.is_closed = True
        self.rotation.closed_at = timezone.now()
        self.rotation.save()
        for e in self.rotation.entries.all():
            e.update_share_totals()

        summary = self.rotation.summary

        self.assertEqual(summary.count(), 1)

        row = summary.first()

        self.assertEqual(row['user'], self.testuser.pk)
        self.assertEqual(row['helped_setups'], 0)
        self.assertEqual(row['estimated_total'], 1_000_000_000)
        self.assertEqual(row['actual_total'], 900_000_000)

    def test_days_since(self):
        self.assertEqual(self.rotation.days_since, 0)

    def test_sales_percentage_open(self):
        self.assertEqual(self.rotation.sales_percentage, 0)

    def test_sales_percentage_closed(self):
        self.rotation.actual_total = 900_000_000
        self.rotation.is_closed = True
        self.rotation.closed_at = timezone.now()
        self.rotation.save()
        for e in self.rotation.entries.all():
            e.update_share_totals()

        self.assertAlmostEqual(self.rotation.sales_percentage, 0.9)

    def test_estimated_total(self):
        self.assertAlmostEqual(self.rotation.estimated_total, 1_000_000_000.0)

    def test_str(self):
        self.assertEqual(str(self.rotation), f'{self.rotation.pk} {self.rotation.name}')
