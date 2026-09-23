from django.db import migrations, models
from django.db.models.functions import Coalesce


def site_count_to_range(apps, schema_editor):
    EntryCharacter = apps.get_model("allianceauth_pve", "EntryCharacter")
    EntryCharacter.objects.filter(site_count__gt=0).update(
        first_site=1, last_site=models.F("site_count")
    )


def range_to_site_count(apps, schema_editor):
    EntryCharacter = apps.get_model("allianceauth_pve", "EntryCharacter")
    EntryCharacter.objects.update(
        site_count=Coalesce(
            models.F("last_site") - models.F("first_site") + 1, 0
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ("allianceauth_pve", "0025_entrycharacter_relative_value"),
    ]

    operations = [
        migrations.AddField(
            model_name="entrycharacter",
            name="first_site",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="entrycharacter",
            name="last_site",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(site_count_to_range, range_to_site_count),
        migrations.RemoveField(
            model_name="entrycharacter",
            name="site_count",
        ),
        migrations.AddConstraint(
            model_name="entrycharacter",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("first_site__isnull", True), ("last_site__isnull", True)),
                    models.Q(
                        ("first_site__gte", 1),
                        ("first_site__isnull", False),
                        ("last_site__gte", models.F("first_site")),
                        ("last_site__isnull", False),
                    ),
                    _connector="OR",
                ),
                name="sites_are_a_valid_range",
            ),
        ),
    ]
