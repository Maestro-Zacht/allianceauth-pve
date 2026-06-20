import re

from django.db.models import Subquery, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import EntryCharacter, Rotation, RotationPreset

item_re = re.compile(r"^\s*(?P<name>[\S \xa0]+)\s+(?P<quantity>[\d.]+)")


def running_averages(user, start_date, end_date=None):
    if end_date is None:
        end_date = timezone.now()

    rotations = (
        Rotation.objects.filter(closed_at__range=(start_date, end_date))
        .get_setup_summary()
        .filter(user=user)
        .values("total_setups")
    )
    result = (
        EntryCharacter.objects.filter(
            entry__rotation__closed_at__range=(start_date, end_date), user=user
        )
        .with_totals()
        .values("user")
        .order_by()
        .annotate(helped_setups=Coalesce(Subquery(rotations[:1]), 0))
        .annotate(estimated_total=Sum("estimated_share_total"))
        .annotate(
            actual_total=Sum("actual_share_total") + Sum("actual_share_total_for_items")
        )
        .values("helped_setups", "estimated_total", "actual_total")
    )

    if result:
        return result[0]
    return {"helped_setups": 0, "estimated_total": 0.0, "actual_total": 0.0}


def ensure_rotation_presets_applied():
    missing_setups = RotationPreset.objects.exclude(
        name__in=Rotation.objects.filter(is_closed=False).values("name")
    )

    for setup in missing_setups:
        r = Rotation.objects.create(
            name=setup.name,
            max_daily_setups=setup.max_daily_setups,
            min_people_share_setup=setup.min_people_share_setup,
            tax_rate=setup.tax_rate,
            tax_rate_loot_items=setup.tax_rate_loot_items,
            priority=setup.priority,
        )

        r.entry_buttons.set(setup.entry_buttons.all())
        r.roles_setups.set(setup.roles_setups.all())


def parse_items_from_inventory(line: str) -> tuple[str, int] | None:
    match = item_re.match(line)
    if match:
        name = match.group("name").strip()
        quantity = int(match.group("quantity").replace(".", ""))
        return name, quantity
    return None
