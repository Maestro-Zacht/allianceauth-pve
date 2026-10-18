from django.db import migrations, models
from django.db.models.fields.json import KT
from django.db.models.functions import Cast, JSONArray, JSONObject


def range_to_sites(apps, schema_editor):
    EntryCharacter = apps.get_model("allianceauth_pve", "EntryCharacter")
    EntryCharacter.objects.filter(first_site__isnull=False).update(
        sites=JSONArray(
            JSONObject(first=models.F("first_site"), last=models.F("last_site"))
        )
    )


def sites_to_range(apps, schema_editor):
    EntryCharacter = apps.get_model("allianceauth_pve", "EntryCharacter")
    EntryCharacter.objects.update(
        first_site=Cast(KT("sites__0__first"), models.PositiveIntegerField()),
        last_site=Cast(KT("sites__0__last"), models.PositiveIntegerField()),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("allianceauth_pve", "0029_remove_entry_site_scaling_coefficient"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="entrycharacter",
            name="sites_are_a_valid_range",
        ),
        migrations.AddField(
            model_name="entrycharacter",
            name="sites",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(range_to_sites, sites_to_range),
        migrations.RemoveField(
            model_name="entrycharacter",
            name="first_site",
        ),
        migrations.RemoveField(
            model_name="entrycharacter",
            name="last_site",
        ),
    ]
