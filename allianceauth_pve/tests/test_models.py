import itertools
import random
from decimal import Decimal

from allianceauth.services.hooks import get_extension_logger
from django.db.models import Sum
from django.test import TestCase
from django.utils import timezone

from allianceauth_pve.models import (
    Entry,
    EntryCharacter,
    EntryLootItem,
    EntryRole,
    FundingProject,
    GeneralRole,
    PveButton,
    RoleSetup,
    Rotation,
    RotationPreset,
    RotationSetupSummary,
    compute_relative_values,
)

from .utils import PveTestBase

logger = get_extension_logger(__name__)


class TestRoleSetup(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rolesetup = RoleSetup.objects.create(name="testrolesetup")

    def test_str(self):
        self.assertEqual(str(self.rolesetup), self.rolesetup.name)


class TestPveButton(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pvebutton = PveButton.objects.create(text="testbutton", amount=1)

    def test_str(self):
        self.assertEqual(str(self.pvebutton), self.pvebutton.text)


class TestGeneralRole(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rolesetup = RoleSetup.objects.create(name="testrolesetup")
        cls.generalrole = GeneralRole.objects.create(
            setup=cls.rolesetup, name="testgeneralrole", value=1
        )

    def test_str(self):
        self.assertEqual(str(self.generalrole), self.generalrole.name)


class TestRotationPreset(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rotationpreset = RotationPreset.objects.create(
            name="testpreset",
        )

    def test_str(self):
        self.assertEqual(
            str(self.rotationpreset), f"{self.rotationpreset.name} rotation preset"
        )


class TestRotation(PveTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser, cls.testcharacter = cls.make_user(
            "aauth_testuser", 2116790529, "aauth_testchar"
        )

        cls.rotation = cls.make_rotation(name="test1rot")

        cls.make_entry(cls.rotation, cls.testuser, cls.testcharacter)

    def test_summary_open(self):
        summary = self.rotation.summary

        self.assertEqual(summary.count(), 1)

        row = summary[0]

        self.assertEqual(row["user"], self.testuser.pk)
        self.assertEqual(row["helped_setups"], 0)
        self.assertEqual(row["estimated_total"], 1_000_000_000)
        self.assertEqual(row["actual_total"], 0)

    def test_summary_closed(self):
        self.rotation.actual_total = 900_000_000
        self.rotation.is_closed = True
        self.rotation.closed_at = timezone.now()
        self.rotation.save()

        summary = self.rotation.summary

        self.assertEqual(summary.count(), 1)

        row = summary[0]

        self.assertEqual(row["user"], self.testuser.pk)
        self.assertEqual(row["helped_setups"], 0)
        self.assertEqual(row["estimated_total"], 1_000_000_000)
        self.assertEqual(row["actual_total"], 900_000_000)

    def test_funding_projects_summary(self):
        project1 = FundingProject.objects.create(
            name="testproject1", goal=1_000_000_000
        )

        project2 = FundingProject.objects.create(
            name="testproject2", goal=1_000_000_000
        )

        rotation2 = self.make_rotation(name="test2rot")

        self.make_entry(
            self.rotation,
            self.testuser,
            self.testcharacter,
            funding_project=project1,
            funding_percentage=50,
        )

        self.make_entry(
            rotation2,
            self.testuser,
            self.testcharacter,
            funding_project=project2,
            funding_percentage=50,
        )

        summary = self.rotation.funding_projects_summary

        self.assertEqual(len(summary), 1)
        self.assertIn(project1, summary)

        project_summary = summary[project1]

        self.assertEqual(len(project_summary), 1)

        row = project_summary[0]

        self.assertEqual(row["user"], self.testuser.pk)
        self.assertEqual(row["actual_total"], 0)
        self.assertEqual(row["estimated_total"], 500_000_000)
        self.assertEqual(row["character_name"], self.testcharacter.character_name)
        self.assertEqual(row["character_id"], self.testcharacter.character_id)

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

    def test_str(self):
        self.assertEqual(str(self.rotation), f"{self.rotation.pk} {self.rotation.name}")

    def test_with_number_of_members(self):
        rotation = Rotation.objects.with_number_of_members().get(pk=self.rotation.pk)
        self.assertEqual(rotation.number_of_members, 1)

    def test_with_estimated_total(self):
        rotation = Rotation.objects.with_estimated_total().get(pk=self.rotation.pk)
        self.assertEqual(rotation.estimated_total, 1_000_000_000)

    def test_with_actual_total_from_items(self):
        rotation = Rotation.objects.with_actual_total_from_items().get(
            pk=self.rotation.pk
        )
        self.assertEqual(rotation.actual_total_from_items, 0.0)

    def test_all_summary(self):
        self.assertQuerySetEqual(Rotation.objects.get_setup_summary(), [])

    def test_setup_summary_str(self):
        summary = RotationSetupSummary(
            rotation=self.rotation,
            user=self.testuser,
            entry_date=timezone.now().date(),
            valid_setups=1,
        )
        self.assertEqual(
            str(summary),
            f"Setup summary for {self.testuser} in {self.rotation}",
        )


class TestEntry(PveTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser, cls.testcharacter = cls.make_user(
            "aauth_testuser", 2116790529, "aauth_testchar"
        )

        cls.testuser2, cls.testcharacter2 = cls.make_user(
            "aauth_testuser2", 795853496, "aauth_testchar2"
        )

        cls.testuser3, cls.testcharacter3 = cls.make_user(
            "aauth_testuser3", 781335233, "aauth_testchar3"
        )

        cls.rotation = cls.make_rotation(name="test1rot", tax_rate=10.0)

        cls.entry, cls.role, cls.share = cls.make_entry(
            cls.rotation, cls.testuser, cls.testcharacter, site_count=2
        )

        cls.funding_project = FundingProject.objects.create(
            name="testproject", goal=100_000_000
        )

    def test_str(self):
        self.assertEqual(str(self.entry), f"Entry {self.entry.pk} in {self.rotation}")

    def test_share_str(self):
        self.assertEqual(str(self.share), f"{self.testcharacter} in {self.entry}")

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
        for (
            count1,
            count2,
            count3,
            value1,
            value2,
            value3,
        ) in itertools.combinations_with_replacement(range(6), 6):
            total_count = count1 + count2 + count3
            total_roles = value1 + value2 + value3
            total_value = value1 * count1 + value2 * count2 + value3 * count3
            if total_count > 0 and total_roles > 0 and total_value > 0:
                estimated_total = random.randint(100_000_000, 10_000_000_000)

                entry, _, share1 = self.make_entry(
                    self.rotation,
                    self.testuser,
                    self.testcharacter,
                    role_name="role1",
                    role_value=value1,
                    site_count=count1,
                    estimated_total=estimated_total,
                )

                role2 = EntryRole.objects.create(
                    entry=entry, name="role2", value=value2
                )
                role3 = EntryRole.objects.create(
                    entry=entry, name="role3", value=value3
                )

                share2 = self.make_share(
                    entry,
                    self.testuser2,
                    self.testcharacter2,
                    role2,
                    site_count=count2,
                )
                share3 = self.make_share(
                    entry,
                    self.testuser3,
                    self.testcharacter3,
                    role3,
                    site_count=count3,
                )

                self.assertTrue(Entry.objects.filter(pk=entry.pk).exists())

                share1 = EntryCharacter.objects.with_totals().get(pk=share1.pk)
                share2 = EntryCharacter.objects.with_totals().get(pk=share2.pk)
                share3 = EntryCharacter.objects.with_totals().get(pk=share3.pk)

                self.assertAlmostEqual(
                    float(share1.estimated_share_total),
                    estimated_total * 0.9 * count1 * value1 / total_value,
                    places=2,
                )
                self.assertAlmostEqual(
                    float(share2.estimated_share_total),
                    estimated_total * 0.9 * count2 * value2 / total_value,
                    places=2,
                )
                self.assertAlmostEqual(
                    float(share3.estimated_share_total),
                    estimated_total * 0.9 * count3 * value3 / total_value,
                    places=2,
                )

                sum_estimated = entry.ratting_shares.with_totals().aggregate(
                    val=Sum("estimated_share_total")
                )["val"]
                self.assertAlmostEqual(
                    float(sum_estimated), entry.estimated_total_after_tax, places=2
                )

                self.assertEqual(share1.actual_share_total, 0)
                self.assertEqual(share2.actual_share_total, 0)
                self.assertEqual(share3.actual_share_total, 0)

        # funding project

        _, _, share1 = self.make_entry(
            self.rotation,
            self.testuser,
            self.testcharacter,
            estimated_total=estimated_total,
            funding_project=self.funding_project,
            funding_percentage=50,
        )

        share1 = EntryCharacter.objects.with_totals().get(pk=share1.pk)

        self.assertAlmostEqual(
            float(share1.estimated_share_total), estimated_total * 0.9 * 0.5, places=2
        )
        # The two halves are now decimals rather than truncated whole ISK, so they
        # are exactly equal instead of equal-after-int().
        self.assertEqual(share1.estimated_funding_amount, share1.estimated_share_total)

    def test_estimated_funding_total(self):
        entry, _, _ = self.make_entry(
            self.rotation,
            self.testuser,
            self.testcharacter,
            funding_project=self.funding_project,
            funding_percentage=50,
        )

        self.assertEqual(entry.estimated_funding_total, 450_000_000)


class TestComputeRelativeValues(TestCase):
    def test_sums_to_exactly_one(self):
        for weights in (
            [1],
            [1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [7, 11, 13],
            [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5],
            list(range(1, 51)),
            [1] * 50,
        ):
            with self.subTest(weights=weights):
                values = compute_relative_values(weights)

                self.assertEqual(len(values), len(weights))
                self.assertEqual(sum(values), Decimal(1))
                for value in values:
                    self.assertGreaterEqual(value, Decimal(0))
                    self.assertLessEqual(value, Decimal(1))

    def test_zero_weights(self):
        self.assertEqual(compute_relative_values([0, 0, 0]), [Decimal(0)] * 3)

    def test_empty(self):
        self.assertEqual(compute_relative_values([]), [])

    def test_proportional(self):
        self.assertEqual(
            compute_relative_values([1, 3]),
            [Decimal("0.25"), Decimal("0.75")],
        )

    def test_residual_lands_on_the_largest_weight(self):
        # 1/3 + 1/3 + 1/3 quantized leaves 1e-20 unallocated; it must not be
        # dropped, and it must go to the biggest share.
        values = compute_relative_values([1, 1, 10])
        self.assertEqual(sum(values), Decimal(1))
        self.assertEqual(max(values), values[2])


class TestShareTotalsAreExact(PveTestBase):
    """The stored fractions sum to 1, so every derived total sums to its entry."""

    ENTRY_TOTAL = 999_999_999_999
    AFTER_TAX = Decimal(999_999_999_999) * Decimal("0.875")

    @classmethod
    def setUpTestData(cls):
        cls.users = [
            cls.make_user(f"aauth_exact{i}", 93000100 + i, f"aauth_exactchar{i}")
            for i in range(3)
        ]

    def make_entry_with_three_equal_shares(self, rotation, **entry_kwargs):
        entry, _, _ = self.make_entry(
            rotation, *self.users[0], role_name="role0", role_value=10, **entry_kwargs
        )
        for i, (user, char) in enumerate(self.users[1:], start=1):
            role = EntryRole.objects.create(entry=entry, name=f"role{i}", value=10)
            self.make_share(entry, user, char, role)
        return entry

    def test_relative_values_sum_to_one(self):
        rotation = self.make_rotation(name="exactrot", tax_rate=12.5)
        entry = self.make_entry_with_three_equal_shares(
            rotation, estimated_total=self.ENTRY_TOTAL
        )

        self.assertEqual(
            entry.ratting_shares.aggregate(val=Sum("relative_value"))["val"],
            Decimal(1),
        )

    def test_estimated_share_total_sums_exactly(self):
        rotation = self.make_rotation(name="exactrot", tax_rate=12.5)
        entry = self.make_entry_with_three_equal_shares(
            rotation, estimated_total=self.ENTRY_TOTAL
        )

        total = entry.ratting_shares.with_totals().aggregate(
            val=Sum("estimated_share_total")
        )["val"]

        self.assertEqual(total, self.AFTER_TAX)

    def test_funded_shares_and_funding_sum_exactly(self):
        rotation = self.make_rotation(name="exactrot", tax_rate=12.5)
        project = FundingProject.objects.create(name="exactproject", goal=1)
        entry = self.make_entry_with_three_equal_shares(
            rotation,
            estimated_total=self.ENTRY_TOTAL,
            funding_project=project,
            funding_percentage=40,
        )

        totals = entry.ratting_shares.with_totals().aggregate(
            shares=Sum("estimated_share_total"),
            funding=Sum("estimated_funding_amount"),
        )

        self.assertEqual(totals["shares"], self.AFTER_TAX * Decimal("0.6"))
        self.assertEqual(totals["funding"], self.AFTER_TAX * Decimal("0.4"))
        self.assertEqual(totals["shares"] + totals["funding"], self.AFTER_TAX)

    def test_items_only_rotation(self):
        """``estimated_total == 0`` must not divide by zero in the actual totals."""
        rotation = self.make_rotation(
            name="itemsonly", tax_rate=12.5, tax_rate_loot_items=10.0, actual_total=0
        )
        entry = self.make_entry_with_three_equal_shares(rotation, estimated_total=0)
        item = self.make_item(99500002, "Items Only")
        self.make_loot_item(entry, item, quantity=3, sale_price=1_000.0)

        totals = entry.ratting_shares.with_totals().aggregate(
            estimated=Sum("estimated_share_total"),
            actual=Sum("actual_share_total"),
            items=Sum("actual_share_total_for_items"),
        )

        self.assertEqual(totals["estimated"], Decimal(0))
        self.assertEqual(totals["actual"], Decimal(0))
        self.assertEqual(totals["items"], Decimal(2700))


class TestEntryLootItem(PveTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser, cls.testcharacter = cls.make_user(
            "aauth_testuser", 2116790529, "aauth_testchar"
        )

        cls.rotation = cls.make_rotation(name="test1rot", tax_rate_loot_items=10.0)

        cls.entry, _, _ = cls.make_entry(cls.rotation, cls.testuser, cls.testcharacter)

        cls.item = cls.make_item(99500001, "Loot Item")

        cls.loot_item = cls.make_loot_item(
            cls.entry, cls.item, quantity=2, sale_price=100.0
        )

    def test_str(self):
        self.assertEqual(str(self.loot_item), f"{self.item} x2")

    def test_manager_with_total_after_tax(self):
        loot_item = EntryLootItem.objects.with_total_after_tax().get(
            pk=self.loot_item.pk
        )
        self.assertAlmostEqual(loot_item.total_after_tax, 180.0)


class TestEntryRole(PveTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser, cls.testcharacter = cls.make_user(
            "aauth_testuser", 2116790529, "aauth_testchar"
        )

        cls.rotation = cls.make_rotation(name="test1rot", tax_rate=10.0)

        entry, cls.role1, _ = cls.make_entry(
            cls.rotation,
            cls.testuser,
            cls.testcharacter,
            role_name="testrole1",
            role_value=1,
        )

        cls.role2 = EntryRole.objects.create(entry=entry, name="testrole2", value=2)

    def test_str(self):
        self.assertEqual(str(self.role1), self.role1.name)

    def test_approximate_percentage(self):
        self.assertAlmostEqual(self.role1.approximate_percentage, (1 / 3) * 100)
        self.assertAlmostEqual(self.role2.approximate_percentage, (2 / 3) * 100)


class TestFundingProject(PveTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser, cls.testcharacter = cls.make_user(
            "aauth_testuser", 2116790529, "aauth_testchar"
        )

        cls.funding_project: FundingProject = FundingProject.objects.create(
            name="testproject", goal=1_000_000_000
        )

        cls.rotation = cls.make_rotation(name="test1rot", tax_rate=0.0)

        cls.entry, _, cls.share = cls.make_entry(
            cls.rotation,
            cls.testuser,
            cls.testcharacter,
            funding_project=cls.funding_project,
            funding_percentage=50,
            site_count=2,
        )

        cls.rotation.is_closed = True
        cls.rotation.closed_at = timezone.now()
        cls.rotation.actual_total = 1_000_000_000
        cls.rotation.save()

    def test_str(self):
        self.assertEqual(str(self.funding_project), self.funding_project.name)

    def test_with_contributions_to(self):
        self.make_entry(self.rotation, self.testuser, self.testcharacter, site_count=2)

        self.make_entry(
            self.rotation,
            self.testuser,
            self.testcharacter,
            funding_project=self.funding_project,
            funding_percentage=0,
            site_count=2,
        )

        self.assertQuerySetEqual(
            EntryCharacter.objects.with_contributions_to(
                self.funding_project, rotation_closed=True
            ),
            [self.share.pk],
            transform=lambda x: x.pk,
        )

        open_rotation = self.make_rotation(name="test1rot", tax_rate=0.0)

        _, _, share_open = self.make_entry(
            open_rotation,
            self.testuser,
            self.testcharacter,
            funding_project=self.funding_project,
            funding_percentage=10,
            site_count=2,
        )

        self.assertQuerySetEqual(
            EntryCharacter.objects.with_contributions_to(
                self.funding_project, rotation_closed=False
            ),
            [share_open.pk],
            transform=lambda x: x.pk,
        )

        self.assertQuerySetEqual(
            EntryCharacter.objects.with_contributions_to(self.funding_project),
            [share_open.pk, self.share.pk],
            transform=lambda x: x.pk,
            ordered=False,
        )

    def test_properties(self):
        self.assertEqual(self.funding_project.current_total, 500_000_000)

        self.assertEqual(self.funding_project.actual_percentage, 50)

        self.assertEqual(self.funding_project.days_since, 0)

        self.assertEqual(self.funding_project.num_participants, 1)

        self.assertDictEqual(
            self.funding_project.summary[0],
            {
                "user": self.testuser.pk,
                "actual_total": 500_000_000,
                "estimated_total": 500_000_000,
                "actual_total_from_items": 0,
            },
        )

        del self.funding_project.summary

        self.assertFalse(self.funding_project.has_open_contributions)

        rotation_open = self.make_rotation(name="test1rot", tax_rate=0.0)

        self.make_entry(
            rotation_open,
            self.testuser,
            self.testcharacter,
            funding_project=self.funding_project,
            funding_percentage=10,
        )

        self.assertDictEqual(
            self.funding_project.summary[0],
            {
                "user": self.testuser.pk,
                "actual_total": 500_000_000,
                "estimated_total": 600_000_000,
                "actual_total_from_items": 0,
            },
        )

        self.assertEqual(self.funding_project.estimated_total, 600_000_000)

        self.assertAlmostEqual(
            float(self.funding_project.estimated_missing_percentage), 10.0
        )

        self.assertAlmostEqual(float(self.funding_project.total_percentage), 60.0)

        self.assertEqual(self.funding_project.html_actual_percentage_width, 50)

        self.assertEqual(self.funding_project.html_estimated_percentage_width, 10)

        self.assertTrue(self.funding_project.has_open_contributions)

        self.assertIsNone(self.funding_project.completed_at)

        self.funding_project.completed_at = timezone.now() + timezone.timedelta(days=1)
        self.funding_project.save()

        self.assertEqual(self.funding_project.completed_in_days, 1)

    def test_affected_by(self):
        project2 = FundingProject.objects.create(
            name="testproject2", goal=1_000_000_000
        )

        rotation2 = self.make_rotation(name="test2rot", tax_rate=0.0)

        self.make_entry(
            rotation2,
            self.testuser,
            self.testcharacter,
            funding_project=project2,
            funding_percentage=50,
            site_count=2,
        )

        self.assertQuerySetEqual(
            FundingProject.objects.affected_by(rotation2),
            [project2.pk],
            transform=lambda x: x.pk,
        )
