from django.test import TestCase
from django.utils import timezone

from allianceauth.tests.auth_utils import AuthUtils

from ..models import GeneralRole, Rotation, Entry, EntryCharacter, EntryRole, RoleSetup, PveButton


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


class TestGeneralRole(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.rolesetup = RoleSetup.objects.create(name='testrolesetup')
        cls.generalrole = GeneralRole.objects.create(
            setup=cls.rolesetup,
            name='testgeneralrole',
            value=1
        )

    def test_str(self):
        self.assertEqual(str(self.generalrole), self.generalrole.name)


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


class TestEntry(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.testuser2 = AuthUtils.create_user('aauth_testuser2')
        cls.testcharacter2 = AuthUtils.add_main_character_2(cls.testuser2, 'aauth_testchar2', 795853496)

        cls.testuser3 = AuthUtils.create_user('aauth_testuser3')
        cls.testcharacter3 = AuthUtils.add_main_character_2(cls.testuser3, 'aauth_testchar3', 781335233)

        cls.rotation: Rotation = Rotation.objects.create(
            name='test1rot',
            tax_rate=10.0
        )

        cls.entry: Entry = Entry.objects.create(
            rotation=cls.rotation,
            created_by=cls.testuser,
            estimated_total=1_000_000_000.0
        )

        cls.role = EntryRole.objects.create(
            entry=cls.entry,
            name='testrole1',
            value=1
        )

        cls.share: EntryCharacter = EntryCharacter.objects.create(
            entry=cls.entry,
            user=cls.testuser,
            user_character=cls.testcharacter,
            role=cls.role,
            site_count=1,
            helped_setup=False
        )

        cls.entry.update_share_totals()

    def test_total_shares_count(self):
        self.assertEqual(self.entry.total_shares_count, 1)

    def test_estimated_total_after_tax(self):
        self.assertAlmostEqual(self.entry.estimated_total_after_tax, 900_000_000.0)

    def test_actual_total_after_tax(self):
        self.rotation.actual_total = 900_000_000
        self.rotation.is_closed = True
        self.rotation.closed_at = timezone.now()
        self.rotation.save()
        for e in self.rotation.entries.all():
            e.update_share_totals()

        self.assertAlmostEqual(self.entry.actual_total_after_tax, 810_000_000.0)

    def test_update_share_totals_valid(self):
        newshare1 = EntryCharacter.objects.create(
            entry=self.entry,
            user=self.testuser2,
            user_character=self.testcharacter2,
            role=self.role,
            site_count=1,
            helped_setup=False
        )

        newshare2 = EntryCharacter.objects.create(
            entry=self.entry,
            user=self.testuser3,
            user_character=self.testcharacter3,
            role=self.role,
            site_count=1,
            helped_setup=True
        )

        self.entry.update_share_totals()

        self.assertAlmostEqual(self.share.estimated_share_total, 10**9 / 3)
        self.assertAlmostEqual(newshare1.estimated_share_total, 10**9 / 3)
        self.assertAlmostEqual(newshare2.estimated_share_total, 10**9 / 3)

        self.assertEqual(self.share.actual_share_total, 0)
        self.assertEqual(newshare1.actual_share_total, 0)
        self.assertEqual(newshare2.actual_share_total, 0)

    def test_update_share_totals_0_shares(self):
        self.share.delete()
        self.entry.update_share_totals()
        self.assertEqual(self.rotation.entries.count(), 0)

    def test_update_share_totals_0_roles(self):
        self.role.delete()
        self.entry.update_share_totals()
        self.assertEqual(self.rotation.entries.count(), 0)


class TestEntryRole(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.rotation: Rotation = Rotation.objects.create(
            name='test1rot',
            tax_rate=10.0
        )

        entry: Entry = Entry.objects.create(
            rotation=cls.rotation,
            created_by=cls.testuser,
            estimated_total=1_000_000_000.0
        )

        cls.role1: EntryRole = EntryRole.objects.create(
            entry=entry,
            name='testrole1',
            value=1
        )

        cls.role2: EntryRole = EntryRole.objects.create(
            entry=entry,
            name='testrole2',
            value=2
        )

    def test_str(self):
        self.assertEqual(str(self.role1), self.role1.name)

    def test_approximate_percentage(self):
        self.assertAlmostEqual(self.role1.approximate_percentage, 100 / 3)
        self.assertAlmostEqual(self.role2.approximate_percentage, 200 / 3)
