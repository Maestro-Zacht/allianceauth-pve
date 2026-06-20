from typing import TYPE_CHECKING, ClassVar

from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger
from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from eve_sde.models import ItemType

logger = get_extension_logger(__name__)


class General(models.Model):  # noqa: DJ008
    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("access_pve", "Access PvE: Can access pve pages and be added in entries"),
            ("manage_entries", "Manage Entries: Can do CRUD operations with entries"),
            (
                "manage_rotations",
                "Manage Rotations: Can do CRUD operations with rotations",
            ),
            (
                "manage_funding_projects",
                "Manage Funding Projects: Can do CRUD operations with funding projects",
            ),
        )


class RotationQueryset(models.QuerySet):
    def get_setup_summary(self):
        return (
            RotationSetupSummary.objects.filter(rotation__in=self)
            .order_by()
            .values("user")
            .annotate(total_setups=Coalesce(models.Sum("valid_setups"), 0))
        )


class RotationManager(models.Manager):
    def get_queryset(self):
        return RotationQueryset(self.model, using=self._db)

    def get_setup_summary(self):
        return self.get_queryset().get_setup_summary()


class EntryCharacterQueryset(models.QuerySet):
    def with_totals(self):
        total_values = (
            EntryCharacter.objects.filter(entry_id=models.OuterRef("entry_id"))
            .annotate(weight_value=models.F("site_count") * models.F("role__value"))
            .values("entry")
            .annotate(total_value=models.Sum("weight_value"))
            .values("total_value")
        )

        rotation_estimated_total = (
            Entry.objects.filter(rotation=models.OuterRef("entry__rotation"))
            .values("rotation")
            .annotate(estimated_total=models.Sum("estimated_total"))
            .values("estimated_total")
        )

        entry_item_total = (
            EntryLootItem.objects.filter(entry_id=models.OuterRef("entry_id"))
            .annotate(item_total=models.F("quantity") * models.F("sale_price"))
            .values("entry")
            .annotate(entry_total=models.Sum("item_total"))
            .values("entry_total")
        )

        return (
            self.annotate(
                share_total=(
                    models.F("entry__estimated_total")
                    * (100 - models.F("entry__rotation__tax_rate"))
                    / 100
                    * models.F("site_count")
                    * models.F("role__value")
                    / models.Subquery(total_values, output_field=models.FloatField())
                )
            )
            .annotate(
                estimated_share_total=models.Case(
                    models.When(
                        entry__funding_project__isnull=True,
                        then=models.F("share_total"),
                    ),
                    default=models.F("share_total")
                    * (100 - models.F("entry__funding_percentage"))
                    / 100,
                )
            )
            .annotate(
                estimated_funding_amount=models.Case(
                    models.When(
                        entry__funding_project__isnull=True,
                        then=models.Value(
                            0, output_field=models.PositiveBigIntegerField()
                        ),
                    ),
                    default=models.ExpressionWrapper(
                        models.F("share_total") - models.F("estimated_share_total"),
                        output_field=models.PositiveBigIntegerField(),
                    ),
                )
            )
            .annotate(
                share_total_for_items=Coalesce(
                    models.Subquery(entry_item_total)
                    * (100 - models.F("entry__rotation__tax_rate_loot_items"))
                    / 100
                    * models.F("site_count")
                    * models.F("role__value")
                    / models.Subquery(total_values, output_field=models.FloatField()),
                    0.0,
                )
            )
            .annotate(
                actual_share_total=models.F("estimated_share_total")
                * models.F("entry__rotation__actual_total")
                / models.Subquery(rotation_estimated_total)
            )
            .annotate(
                actual_share_total_for_items=models.Case(
                    models.When(
                        entry__funding_project__isnull=True,
                        then=models.F("share_total_for_items"),
                    ),
                    default=models.F("share_total_for_items")
                    * (100 - models.F("entry__funding_percentage"))
                    / 100,
                )
            )
            .annotate(
                actual_funding_amount=models.F("estimated_funding_amount")
                * models.F("entry__rotation__actual_total")
                / models.Subquery(rotation_estimated_total)
            )
            .annotate(
                actual_funding_amount_for_items=models.Case(
                    models.When(
                        entry__funding_project__isnull=True,
                        then=models.Value(
                            0, output_field=models.PositiveBigIntegerField()
                        ),
                    ),
                    default=models.ExpressionWrapper(
                        models.F("share_total_for_items")
                        - models.F("actual_share_total_for_items"),
                        output_field=models.PositiveBigIntegerField(),
                    ),
                )
            )
        )

    def with_contributions_to(
        self, funding_project, *, rotation_closed: bool | None = None
    ):
        res = self.filter(
            entry__funding_percentage__gt=0, entry__funding_project=funding_project
        )
        if rotation_closed is not None:
            res = res.filter(entry__rotation__is_closed=rotation_closed)
        return res


class EntryCharacterManager(models.Manager):
    def get_queryset(self):
        return EntryCharacterQueryset(self.model, using=self._db)

    def with_totals(self):
        return self.get_queryset().with_totals()

    def with_contributions_to(
        self, funding_project, *, rotation_closed: bool | None = None
    ):
        return self.get_queryset().with_contributions_to(
            funding_project, rotation_closed=rotation_closed
        )


class EntryQueryset(models.QuerySet):
    def with_items_total(self):
        items_qs = (
            EntryLootItem.objects.filter(entry_id=models.OuterRef("pk"))
            .annotate(
                item_total=(
                    models.F("quantity")
                    * models.F("sale_price")
                    * (100.0 - models.F("entry__rotation__tax_rate_loot_items"))
                    / 100.0
                )
            )
            .values("entry")
            .annotate(entry_total=models.Sum("item_total"))
            .values("entry_total")
        )
        return self.annotate(
            actual_total_from_items=Coalesce(models.Subquery(items_qs), 0.0)
        )


class EntryManager(models.Manager):
    def get_queryset(self):
        return EntryQueryset(self.model, using=self._db)

    def with_items_total(self):
        return self.get_queryset().with_items_total()


class EntryLootItemQueryset(models.QuerySet):
    def with_total_after_tax(self):
        return self.annotate(
            total_after_tax=(
                models.F("quantity")
                * models.F("sale_price")
                * (100.0 - models.F("entry__rotation__tax_rate_loot_items"))
                / 100.0
            )
        )


class EntryLootItemManager(models.Manager):
    def get_queryset(self):
        return EntryLootItemQueryset(self.model, using=self._db)

    def with_total_after_tax(self):
        return self.get_queryset().with_total_after_tax()


class PveButton(models.Model):
    text = models.CharField(max_length=16, unique=True)
    amount = models.BigIntegerField()

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return self.text


class RoleSetup(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return self.name


class GeneralRole(models.Model):
    setup = models.ForeignKey(RoleSetup, on_delete=models.CASCADE, related_name="roles")

    name = models.CharField(max_length=64)
    value = models.PositiveIntegerField(
        _("relative role value"),
        help_text=_(
            "Relative role value. Share values are computed using this field. If there are 2 roles with 10 and 15, they'll receive 10/25 and 15/25 of the share value."
        ),
    )

    class Meta:
        default_permissions = ()
        constraints = (
            models.UniqueConstraint(
                fields=["setup", "name"], name="unique_role_name_per_setup"
            ),
        )

    def __str__(self) -> str:
        return self.name


class RotationPreset(models.Model):
    name = models.CharField(max_length=128, unique=True)

    max_daily_setups = models.PositiveSmallIntegerField(
        default=1,
        help_text=_(
            "The maximum number of helped setup per day. If more are submitted, only this number is counted. 0 for deactivating helped setups."
        ),
    )
    min_people_share_setup = models.PositiveSmallIntegerField(
        default=3,
        help_text=_(
            "The minimum number of users in an entry to consider the helped setup valid."
        ),
    )

    tax_rate = models.FloatField(default=0, help_text=_("Tax rate in percentage"))
    tax_rate_loot_items = models.FloatField(
        default=0, help_text=_("Tax rate for loot items in percentage")
    )
    priority = models.IntegerField(
        default=100,
        help_text=_(
            "Ordering priority. The higher priorities are in the first positions."
        ),
    )

    entry_buttons = models.ManyToManyField(
        PveButton,
        related_name="+",
        help_text=_("Button to be shown in the Entry form."),
        blank=True,
    )
    roles_setups = models.ManyToManyField(
        RoleSetup,
        related_name="+",
        help_text=_("Setup avaiable for loading in the Entry form."),
        blank=True,
    )

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return gettext("%(name)s rotation preset") % {"name": self.name}


class Rotation(models.Model):
    name = models.CharField(max_length=128)

    actual_total = models.PositiveBigIntegerField(default=0)

    max_daily_setups = models.PositiveSmallIntegerField(
        default=1,
        help_text=_(
            "The maximum number of helped setup per day. If more are submitted, only this number is counted. 0 for deactivating helped setups."
        ),
    )
    min_people_share_setup = models.PositiveSmallIntegerField(
        default=3,
        help_text=_(
            "The minimum number of users in an entry to consider the helped setup valid."
        ),
    )

    tax_rate = models.FloatField(default=0, help_text=_("Tax rate in percentage"))
    tax_rate_loot_items = models.FloatField(default=0)
    is_closed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    priority = models.IntegerField(
        default=100,
        help_text=_(
            "Ordering priority. The higher priorities are in the first positions."
        ),
    )

    entry_buttons = models.ManyToManyField(
        PveButton,
        related_name="+",
        help_text=_("Button to be shown in the Entry form."),
        blank=True,
    )
    roles_setups = models.ManyToManyField(
        RoleSetup,
        related_name="+",
        help_text=_("Setup avaiable for loading in the Entry form."),
        blank=True,
    )

    objects: ClassVar[RotationManager] = RotationManager()

    class Meta:
        default_permissions = ()

    def __str__(self):
        return f"{self.pk} {self.name}"

    @cached_property
    def funding_projects_summary(self):
        res = {}

        projects = FundingProject.objects.filter(
            models.Exists(
                Entry.objects.filter(
                    rotation=self,
                    funding_project=models.OuterRef("pk"),
                    funding_percentage__gt=0,
                )
            )
        )

        for project in projects:
            res[project] = (
                EntryCharacter.objects.filter(entry__rotation=self)
                .with_contributions_to(project)
                .with_totals()
                .order_by()
                .values("user")
                .annotate(estimated_total=models.Sum("estimated_funding_amount"))
                .annotate(actual_total=models.Sum("actual_funding_amount"))
                .annotate(
                    actual_total_from_items=Coalesce(
                        models.Sum("actual_funding_amount_for_items"), 0
                    )
                )
                .order_by("-estimated_total")
                .values(
                    "user",
                    "estimated_total",
                    "actual_total",
                    "actual_total_from_items",
                    character_name=models.F(
                        "user__profile__main_character__character_name"
                    ),
                    character_id=models.F(
                        "user__profile__main_character__character_id"
                    ),
                    main_character_id=models.F(
                        "user__profile__main_character__character_id"
                    ),
                )
            )

        return res

    @property
    def summary(self):
        setup_summary = (
            Rotation.objects.filter(pk=self.pk)
            .get_setup_summary()
            .filter(user_id=models.OuterRef("user_id"))
            .values("total_setups")
        )

        return (
            EntryCharacter.objects.filter(entry__rotation=self)
            .with_totals()
            .order_by()
            .values("user")
            .annotate(helped_setups=Coalesce(models.Subquery(setup_summary[:1]), 0))
            .annotate(estimated_total=models.Sum("estimated_share_total"))
            .annotate(actual_total=models.Sum("actual_share_total"))
            .annotate(
                actual_total_from_items=models.Sum("actual_share_total_for_items")
            )
        )

    @property
    def days_since(self):
        return (timezone.now() - self.created_at).days

    @property
    def sales_percentage(self):
        return (
            0.0
            if not self.actual_total or self.estimated_total == 0
            else self.actual_total / self.estimated_total
        )

    @cached_property
    def estimated_total(self):
        return self.entries.aggregate(
            estimated_total=Coalesce(models.Sum("estimated_total"), 0)
        )["estimated_total"]

    @cached_property
    def num_participants(self):
        return EntryCharacter.objects.filter(entry__rotation=self).aggregate(
            num=models.Count("user", distinct=True)
        )["num"]

    @property
    def actual_total_from_items(self):
        return (
            EntryLootItem.objects.filter(entry__rotation=self)
            .annotate(item_total=models.F("quantity") * models.F("sale_price"))
            .aggregate(total=Coalesce(models.Sum("item_total"), 0.0))["total"]
        )


class EntryCharacter(models.Model):
    entry = models.ForeignKey(
        "Entry", on_delete=models.CASCADE, related_name="ratting_shares"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="ratting_shares",
    )
    user_character = models.ForeignKey(
        EveCharacter, on_delete=models.RESTRICT, related_name="ratting_shares"
    )
    role = models.ForeignKey(
        "EntryRole", on_delete=models.RESTRICT, related_name="shares"
    )

    site_count = models.PositiveIntegerField(default=1)
    helped_setup = models.BooleanField(default=False)

    objects: ClassVar[EntryCharacterManager] = EntryCharacterManager()

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return f"{self.user_character} in {self.entry}"


class Entry(models.Model):
    rotation = models.ForeignKey(
        Rotation, on_delete=models.CASCADE, related_name="entries"
    )
    estimated_total = models.PositiveBigIntegerField(default=0)

    funding_project = models.ForeignKey(
        "FundingProject",
        on_delete=models.RESTRICT,
        related_name="entries",
        null=True,
        blank=True,
    )
    funding_percentage = models.PositiveSmallIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name="+"
    )
    updated_at = models.DateTimeField(auto_now=True)

    objects: ClassVar[EntryManager] = EntryManager()

    if TYPE_CHECKING:
        ratting_shares: models.manager.RelatedManager["EntryCharacter"]
        loot_items: models.manager.RelatedManager["EntryLootItem"]
        roles: models.manager.RelatedManager["EntryRole"]

    class Meta:
        default_permissions = ()
        verbose_name = "entry"
        verbose_name_plural = "entries"

    def __str__(self) -> str:
        return f"Entry {self.pk} in {self.rotation}"

    @cached_property
    def total_user_count(self):
        return self.ratting_shares.aggregate(
            val=models.Count("user_id", distinct=True)
        )["val"]

    @cached_property
    def total_site_count(self):
        return self.ratting_shares.aggregate(val=models.Sum("site_count"))["val"]

    @cached_property
    def estimated_total_after_tax(self):
        tax_perc = (100 - self.rotation.tax_rate) / 100
        return self.estimated_total * tax_perc

    @cached_property
    def actual_total_after_tax(self):
        return self.estimated_total_after_tax * self.rotation.sales_percentage

    @cached_property
    def estimated_funding_total(self):
        return (
            0
            if self.funding_project is None or self.funding_percentage == 0
            else self.ratting_shares.with_totals().aggregate(
                tot=models.Sum("estimated_funding_amount")
            )["tot"]
        )


class EntryLootItem(models.Model):
    entry = models.ForeignKey(
        Entry, on_delete=models.CASCADE, related_name="loot_items"
    )

    item = models.ForeignKey(ItemType, on_delete=models.RESTRICT, related_name="+")
    quantity = models.PositiveIntegerField()

    sale_price = models.FloatField(null=True, blank=True)

    objects: ClassVar[EntryLootItemManager] = EntryLootItemManager()

    class Meta:
        default_permissions = ()
        constraints = (
            models.UniqueConstraint(
                fields=["entry", "item"], name="unique_item_per_entry"
            ),
        )

    def __str__(self) -> str:
        return f"{self.item} x{self.quantity}"


class EntryRole(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="roles")

    name = models.CharField(max_length=64)
    value = models.PositiveIntegerField(
        _("relative role value"),
        help_text=_(
            "Relative role value. Share values are computed using this field. If there are 2 roles with 10 and 15, they'll receive 10/25 and 15/25 of the share value."
        ),
    )

    class Meta:
        default_permissions = ()
        constraints = (
            models.UniqueConstraint(
                fields=["entry", "name"], name="unique_role_name_per_entry"
            ),
        )

    def __str__(self) -> str:
        return self.name

    @cached_property
    def approximate_percentage(self):
        return (
            self.value
            * 100
            / (
                EntryRole.objects.filter(entry_id=self.entry_id).aggregate(
                    val=models.Sum("value")
                )["val"]
            )
        )


class RotationSetupSummary(models.Model):
    id = models.BigIntegerField(primary_key=True)
    rotation = models.ForeignKey(
        Rotation, on_delete=models.DO_NOTHING, related_name="+"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name="rotations_stats",
    )
    entry_date = models.DateField()
    valid_setups = models.IntegerField()

    class Meta:
        managed = False  # this is a view, check 0012
        db_table = "allianceauth_pve_setup_summary"
        default_permissions = ()

    def __str__(self) -> str:
        return f"Setup summary for {self.user} in {self.rotation}"


class FundingProjectQueryset(models.QuerySet):
    def affected_by(self, rotation: Rotation):
        return self.filter(
            models.Exists(
                Entry.objects.filter(
                    funding_project_id=models.OuterRef("pk"),
                    rotation=rotation,
                    funding_percentage__gt=0,
                )
            )
        )


class FundingProjectManager(models.Manager):
    def get_queryset(self):
        return FundingProjectQueryset(self.model, using=self._db)

    def affected_by(self, rotation: Rotation):
        return self.get_queryset().affected_by(rotation)


class FundingProject(models.Model):
    name = models.CharField(max_length=128)
    goal = models.PositiveBigIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    objects = FundingProjectManager()

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.name

    @cached_property
    def current_total(self):
        return (
            EntryCharacter.objects.with_contributions_to(self, rotation_closed=True)
            .with_totals()
            .aggregate(
                current_total=Coalesce(
                    models.Sum("actual_funding_amount")
                    + models.Sum("actual_funding_amount_for_items"),
                    0,
                )
            )["current_total"]
        )

    @cached_property
    def estimated_total(self):
        return (
            self.current_total
            + (
                EntryCharacter.objects.with_contributions_to(
                    self, rotation_closed=False
                )
                .with_totals()
                .aggregate(
                    estimated_total=Coalesce(models.Sum("estimated_funding_amount"), 0)
                )["estimated_total"]
            )
        )

    @cached_property
    def actual_percentage(self):
        return self.current_total / self.goal * 100

    @cached_property
    def estimated_missing_percentage(self):
        return (self.estimated_total - self.current_total) / self.goal * 100

    @cached_property
    def total_percentage(self):
        return self.actual_percentage + self.estimated_missing_percentage

    @property
    def html_actual_percentage_width(self):
        return int(self.actual_percentage) if self.actual_percentage <= 100 else 100

    @property
    def html_estimated_percentage_width(self):
        return (
            int(self.estimated_missing_percentage)
            if self.actual_percentage + self.estimated_missing_percentage <= 100
            else 100 - int(self.actual_percentage)
        )

    @property
    def days_since(self):
        return (timezone.now() - self.created_at).days

    @property
    def completed_in_days(self):
        return (
            None
            if self.completed_at is None
            else (self.completed_at - self.created_at).days
        )

    @cached_property
    def num_participants(self) -> int:
        return EntryCharacter.objects.with_contributions_to(self).aggregate(
            num=models.Count("user", distinct=True)
        )["num"]

    @cached_property
    def summary(self):
        estimated_part = (
            EntryCharacter.objects.filter(user=models.OuterRef("user"))
            .with_contributions_to(self, rotation_closed=False)
            .with_totals()
            .order_by()
            .values("user")
            .annotate(estimated_total=models.Sum("estimated_funding_amount"))
            .values("estimated_total")
        )

        return (
            EntryCharacter.objects.with_contributions_to(self)
            .with_totals()
            .order_by()
            .values("user")
            .annotate(actual_total=models.Sum("actual_funding_amount"))
            .annotate(
                actual_total_from_items=Coalesce(
                    models.Sum("actual_funding_amount_for_items"), 0
                )
            )
            .annotate(
                estimated_total=models.F("actual_total")
                + models.F("actual_total_from_items")
                + Coalesce(models.Subquery(estimated_part), 0)
            )
        )

    @property
    def has_open_contributions(self) -> bool:
        return self.entries.filter(rotation__is_closed=False).exists()
