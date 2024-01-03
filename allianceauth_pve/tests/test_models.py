import itertools
import random

from django.test import TestCase
from django.utils import timezone
from django.db.models import Sum

from allianceauth.tests.auth_utils import AuthUtils
from allianceauth.services.hooks import get_extension_logger

from ..models import GeneralRole, Rotation, Entry, EntryCharacter, EntryRole, RoleSetup, PveButton, FundingProject

logger = get_extension_logger(__name__)


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
            estimated_total=1_000_000_000
        )

        role = EntryRole.objects.create(
            entry=entry,
            name='testrole1',
            value=1
        )

        EntryCharacter.objects.create(
            entry=entry,
            user=cls.testuser,
            user_character=cls.testcharacter,
            role=role,
            site_count=1,
            helped_setup=False
        )

    def test_summary_open(self):
        summary = self.rotation.summary

        self.assertEqual(summary.count(), 1)

        row = summary[0]

        self.assertEqual(row['user'], self.testuser.pk)
        self.assertEqual(row['helped_setups'], 0)
        self.assertEqual(row['estimated_total'], 1_000_000_000)
        self.assertEqual(row['actual_total'], 0)

    def test_summary_closed(self):
        self.rotation.actual_total = 900_000_000
        self.rotation.is_closed = True
        self.rotation.closed_at = timezone.now()
        self.rotation.save()

        summary = self.rotation.summary

        self.assertEqual(summary.count(), 1)

        row = summary[0]

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

        self.assertAlmostEqual(self.rotation.sales_percentage, 0.9)

    def test_estimated_total(self):
        self.assertAlmostEqual(self.rotation.estimated_total, 1_000_000_000)

    def test_str(self):
        self.assertEqual(str(self.rotation), f'{self.rotation.pk} {self.rotation.name}')

    def test_all_summary(self):
        self.assertQuerysetEqual(Rotation.objects.get_setup_summary(), [])


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
            estimated_total=1_000_000_000
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
            site_count=2,
            helped_setup=False
        )

        cls.funding_project = FundingProject.objects.create(
            name='testproject',
            goal=100_000_000
        )

    def test_total_user_count(self):
        self.assertEqual(self.entry.total_user_count, 1)

    def test_total_site_count(self):
        self.assertEqual(self.entry.total_site_count, 2)

    def test_estimated_total_after_tax(self):
        self.assertAlmostEqual(self.entry.estimated_total_after_tax, 900_000_000.0)

    def test_actual_total_after_tax(self):
        self.rotation.actual_total = 900_000_000
        self.rotation.is_closed = True
        self.rotation.closed_at = timezone.now()
        self.rotation.save()

        self.assertAlmostEqual(self.entry.actual_total_after_tax, 810_000_000.0)

    def test_with_totals_valid(self):
        for count1, count2, count3, value1, value2, value3 in itertools.combinations_with_replacement(range(6), 6):
            total_count = count1 + count2 + count3
            total_roles = value1 + value2 + value3
            total_value = value1 * count1 + value2 * count2 + value3 * count3
            if total_count > 0 and total_roles > 0 and total_value > 0:
                estimated_total = random.randint(100_000_000, 10_000_000_000)

                entry: Entry = Entry.objects.create(
                    rotation=self.rotation,
                    created_by=self.testuser,
                    estimated_total=estimated_total
                )

                role1: EntryRole = EntryRole.objects.create(
                    entry=entry,
                    name='role1',
                    value=value1
                )
                role2: EntryRole = EntryRole.objects.create(
                    entry=entry,
                    name='role2',
                    value=value2
                )
                role3: EntryRole = EntryRole.objects.create(
                    entry=entry,
                    name='role3',
                    value=value3
                )

                share1: EntryCharacter = EntryCharacter.objects.create(
                    entry=entry,
                    user=self.testuser,
                    user_character=self.testcharacter,
                    role=role1,
                    site_count=count1,
                )
                share2: EntryCharacter = EntryCharacter.objects.create(
                    entry=entry,
                    user=self.testuser2,
                    user_character=self.testcharacter2,
                    role=role2,
                    site_count=count2,
                )
                share3: EntryCharacter = EntryCharacter.objects.create(
                    entry=entry,
                    user=self.testuser3,
                    user_character=self.testcharacter3,
                    role=role3,
                    site_count=count3,
                )

                self.assertTrue(Entry.objects.filter(pk=entry.pk).exists())

                share1 = EntryCharacter.objects.with_totals().get(pk=share1.pk)
                share2 = EntryCharacter.objects.with_totals().get(pk=share2.pk)
                share3 = EntryCharacter.objects.with_totals().get(pk=share3.pk)

                self.assertAlmostEqual(share1.estimated_share_total, estimated_total * 0.9 * count1 * value1 / total_value, places=2)
                self.assertAlmostEqual(share2.estimated_share_total, estimated_total * 0.9 * count2 * value2 / total_value, places=2)
                self.assertAlmostEqual(share3.estimated_share_total, estimated_total * 0.9 * count3 * value3 / total_value, places=2)

                sum_estimated = entry.ratting_shares.with_totals().aggregate(val=Sum('estimated_share_total'))['val']
                self.assertAlmostEqual(sum_estimated, entry.estimated_total_after_tax, places=2)

                self.assertEqual(share1.actual_share_total, 0)
                self.assertEqual(share2.actual_share_total, 0)
                self.assertEqual(share3.actual_share_total, 0)

        # funding project

        entry: Entry = Entry.objects.create(
            rotation=self.rotation,
            created_by=self.testuser,
            estimated_total=estimated_total,
            funding_project=self.funding_project,
            funding_percentage=50,
        )

        role1: EntryRole = EntryRole.objects.create(
            entry=entry,
            name='role1',
            value=1
        )

        share1: EntryCharacter = EntryCharacter.objects.create(
            entry=entry,
            user=self.testuser,
            user_character=self.testcharacter,
            role=role1,
            site_count=1,
        )

        share1 = EntryCharacter.objects.with_totals().get(pk=share1.pk)

        self.assertAlmostEqual(share1.estimated_share_total, estimated_total * 0.9 * 0.5, places=2)
        self.assertEqual(share1.estimated_funding_amount, int(share1.estimated_share_total))

    def test_estimated_funding_total(self):
        entry: Entry = Entry.objects.create(
            rotation=self.rotation,
            created_by=self.testuser,
            estimated_total=1_000_000_000,
            funding_project=self.funding_project,
            funding_percentage=50,
        )

        role1: EntryRole = EntryRole.objects.create(
            entry=entry,
            name='role1',
            value=1
        )

        EntryCharacter.objects.create(
            entry=entry,
            user=self.testuser,
            user_character=self.testcharacter,
            role=role1,
            site_count=1,
        )

        self.assertEqual(entry.estimated_funding_total, 450_000_000)


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
            estimated_total=1_000_000_000
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
        self.assertAlmostEqual(self.role1.approximate_percentage, (1 / 3) * 100)
        self.assertAlmostEqual(self.role2.approximate_percentage, (2 / 3) * 100)


class TestFundingProject(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.funding_project: FundingProject = FundingProject.objects.create(
            name='testproject',
            goal=1_000_000_000
        )

        cls.rotation: Rotation = Rotation.objects.create(
            name='test1rot',
            tax_rate=0.0
        )

        cls.entry: Entry = Entry.objects.create(
            rotation=cls.rotation,
            created_by=cls.testuser,
            estimated_total=1_000_000_000,
            funding_project=cls.funding_project,
            funding_percentage=50,
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
            site_count=2,
            helped_setup=False
        )

        cls.rotation.is_closed = True
        cls.rotation.closed_at = timezone.now()
        cls.rotation.actual_total = 1_000_000_000
        cls.rotation.save()

    def test_str(self):
        self.assertEqual(str(self.funding_project), self.funding_project.name)

    def test_with_contributions_to(self):
        entry2 = Entry.objects.create(
            rotation=self.rotation,
            created_by=self.testuser,
            estimated_total=1_000_000_000,
        )

        EntryCharacter.objects.create(
            entry=entry2,
            user=self.testuser,
            user_character=self.testcharacter,
            role=self.role,
            site_count=2,
            helped_setup=False
        )

        entry3 = Entry.objects.create(
            rotation=self.rotation,
            created_by=self.testuser,
            estimated_total=1_000_000_000,
            funding_project=self.funding_project,
            funding_percentage=0,
        )

        EntryCharacter.objects.create(
            entry=entry3,
            user=self.testuser,
            user_character=self.testcharacter,
            role=self.role,
            site_count=2,
            helped_setup=False
        )

        self.assertQuerysetEqual(
            EntryCharacter.objects.with_contributions_to(self.funding_project, True),
            [self.share.pk],
            transform=lambda x: x.pk
        )

        open_rotation = Rotation.objects.create(
            name='test1rot',
            tax_rate=0.0
        )

        entry4 = Entry.objects.create(
            rotation=open_rotation,
            created_by=self.testuser,
            estimated_total=1_000_000_000,
            funding_project=self.funding_project,
            funding_percentage=10,
        )

        share_open = EntryCharacter.objects.create(
            entry=entry4,
            user=self.testuser,
            user_character=self.testcharacter,
            role=self.role,
            site_count=2,
            helped_setup=False
        )

        self.assertQuerysetEqual(
            EntryCharacter.objects.with_contributions_to(self.funding_project, False),
            [share_open.pk],
            transform=lambda x: x.pk
        )

        self.assertQuerysetEqual(
            EntryCharacter.objects.with_contributions_to(self.funding_project),
            [share_open.pk, self.share.pk],
            transform=lambda x: x.pk,
            ordered=False
        )

    def test_properties(self):
        self.assertEqual(self.funding_project.current_total, 500_000_000)

        self.assertEqual(self.funding_project.actual_percentage, 50)

        self.assertEqual(self.funding_project.days_since, 0)

        self.assertEqual(self.funding_project.num_participants, 1)

        self.assertDictEqual(
            self.funding_project.summary[0],
            {
                'user': self.testuser.pk,
                'actual_total': 500_000_000,
                'estimated_total': 500_000_000
            }
        )

        del self.funding_project.summary

        self.assertFalse(self.funding_project.has_open_contributions)

        rotation_open = Rotation.objects.create(
            name='test1rot',
            tax_rate=0.0
        )

        entry_open = Entry.objects.create(
            rotation=rotation_open,
            created_by=self.testuser,
            estimated_total=1_000_000_000,
            funding_project=self.funding_project,
            funding_percentage=10,
        )

        EntryCharacter.objects.create(
            entry=entry_open,
            user=self.testuser,
            user_character=self.testcharacter,
            role=self.role,
            site_count=1,
            helped_setup=False
        )

        self.assertDictEqual(
            self.funding_project.summary[0],
            {
                'user': self.testuser.pk,
                'actual_total': 500_000_000,
                'estimated_total': 600_000_000
            }
        )

        self.assertEqual(self.funding_project.estimated_total, 600_000_000)

        self.assertAlmostEqual(self.funding_project.estimated_missing_percentage, 10.0)

        self.assertAlmostEqual(self.funding_project.total_percentage, 60.0)

        self.assertEqual(self.funding_project.html_actual_percentage_width, 50)

        self.assertEqual(self.funding_project.html_estimated_percentage_width, 10)

        self.assertTrue(self.funding_project.has_open_contributions)

        self.assertIsNone(self.funding_project.completed_at)

        self.funding_project.completed_at = timezone.now() + timezone.timedelta(days=1)
        self.funding_project.save()

        self.assertEqual(self.funding_project.completed_in_days, 1)

    def test_affected_by(self):
        project2 = FundingProject.objects.create(
            name='testproject2',
            goal=1_000_000_000
        )

        rotation2 = Rotation.objects.create(
            name='test2rot',
            tax_rate=0.0
        )

        entry2 = Entry.objects.create(
            rotation=rotation2,
            created_by=self.testuser,
            estimated_total=1_000_000_000,
            funding_project=project2,
            funding_percentage=50,
        )

        role2 = EntryRole.objects.create(
            entry=entry2,
            name='testrole2',
            value=1
        )

        EntryCharacter.objects.create(
            entry=entry2,
            user=self.testuser,
            user_character=self.testcharacter,
            role=role2,
            site_count=2,
            helped_setup=False
        )

        self.assertQuerysetEqual(FundingProject.objects.affected_by(rotation2), [project2.pk], transform=lambda x: x.pk)
