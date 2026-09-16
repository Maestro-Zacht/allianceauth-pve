import sys
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from itertools import groupby

from django.db import migrations, models

RELATIVE_VALUE_DECIMAL_PLACES = 20
RELATIVE_VALUE_QUANTUM = Decimal(1).scaleb(-RELATIVE_VALUE_DECIMAL_PLACES)


def compute_relative_values(weights):
    """Frozen copy of ``models.compute_relative_values``."""
    total = sum(weights)
    if total == 0:
        return [Decimal(0)] * len(weights)

    with localcontext() as ctx:
        ctx.prec = 40
        values = [
            (Decimal(w) / total).quantize(
                RELATIVE_VALUE_QUANTUM, rounding=ROUND_HALF_EVEN
            )
            for w in weights
        ]

    residual = Decimal(1) - sum(values)
    if residual:
        values[max(range(len(weights)), key=weights.__getitem__)] += residual
    return values


SAVE_CURSOR = "\x1b7"
RESTORE_CURSOR = "\x1b8"
CLEAR_LINE = "\r\x1b[K"


def show_progress(done, total, width=30):
    if not sys.stdout.isatty():
        return

    if done == 0:
        sys.stdout.write(f"{SAVE_CURSOR}\n")

    filled = width * done // total
    sys.stdout.write(
        f"{CLEAR_LINE}    backfilling relative_value "
        f"[{'#' * filled}{'.' * (width - filled)}] {done}/{total}"
    )
    if done == total:
        sys.stdout.write(f"{CLEAR_LINE}{RESTORE_CURSOR}")
    sys.stdout.flush()


def backfill_relative_values(apps, schema_editor):
    EntryCharacter = apps.get_model("allianceauth_pve", "EntryCharacter")

    total = EntryCharacter.objects.count()
    if not total:
        return

    shares = EntryCharacter.objects.order_by("entry_id").values_list(
        "pk", "entry_id", "site_count", "role__value"
    )

    done = 0
    show_progress(done, total)

    for _, entry_shares in groupby(shares, key=lambda share: share[1]):
        entry_shares = list(entry_shares)
        values = compute_relative_values(
            [site_count * role_value for _, _, site_count, role_value in entry_shares]
        )
        EntryCharacter.objects.bulk_update(
            [
                EntryCharacter(pk=share[0], relative_value=value)
                for share, value in zip(entry_shares, values, strict=True)
            ],
            ["relative_value"],
        )

        done += len(entry_shares)
        show_progress(done, total)


class Migration(migrations.Migration):
    dependencies = [
        ("allianceauth_pve", "0024_rotationpreset_tax_rate_loot_items"),
    ]

    operations = [
        migrations.AddField(
            model_name="entrycharacter",
            name="relative_value",
            field=models.DecimalField(
                decimal_places=20, max_digits=21, null=True, verbose_name="relative value"
            ),
        ),
        migrations.RunPython(backfill_relative_values, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="entrycharacter",
            name="relative_value",
            field=models.DecimalField(
                decimal_places=20,
                max_digits=21,
                verbose_name="relative value",
            ),
        ),
        migrations.AddConstraint(
            model_name="entrycharacter",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("relative_value__gte", 0), ("relative_value__lte", 1)
                ),
                name="relative_value_is_a_fraction",
            ),
        ),
    ]
