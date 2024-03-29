# Generated by Django 4.0.8 on 2022-10-14 21:27

from django.db import migrations, models
from django.db.models.functions import Coalesce
from django.conf import settings


def estimated_total(rotation):
    return rotation.entries.aggregate(estimated_total=Coalesce(models.Sum('estimated_total'), 0))['estimated_total']


def sales_percentage(rotation):
    estimated = estimated_total(rotation)
    return 0.00 if not rotation.actual_total or estimated == 0 else rotation.actual_total / estimated


def update_share_totals_legacy(entry, EntryRole):
    sum_sites = entry.ratting_shares.aggregate(val=Coalesce(models.Sum('site_count'), 0))['val']

    entry.roles.alias(char_count=models.Count('shares')).filter(char_count=0).delete()
    num_roles = entry.roles.count()
    if sum_sites == 0 or num_roles == 0:
        entry.delete()
    else:
        entry.save()

        estimated_total_after_tax = entry.estimated_total * (100 - entry.rotation.tax_rate) / 100
        actual_total_after_tax = estimated_total_after_tax * sales_percentage(entry.rotation)

        if settings.DATABASES[entry.ratting_shares.db]['ENGINE'] == 'django.db.backends.mysql':
            total_value = 0
            for role in entry.roles.all():
                total_value += role.shares.annotate(weighted_share_value=models.F('site_count') * models.Value(role.value))\
                    .aggregate(val=models.Sum('weighted_share_value'))['val']

            for role in entry.roles.all():
                role.shares\
                    .annotate(weighted_share_value=models.F('site_count') * models.Value(role.value))\
                    .annotate(relative_value=models.F('weighted_share_value') / models.Value(total_value, output_field=models.FloatField()))\
                    .update(
                        estimated_share_total=models.Value(estimated_total_after_tax) * models.F('relative_value'),
                        actual_share_total=models.Value(actual_total_after_tax) * models.F('relative_value'),
                    )
        else:
            role_val_query = EntryRole.objects.filter(pk=models.OuterRef('role_id')).values('value')

            annotated_shares = entry.ratting_shares\
                .annotate(role_val=models.Subquery(role_val_query))\
                .annotate(weighted_share_value=models.F('site_count') * models.F('role_val'))

            total_value = annotated_shares.aggregate(val=models.Sum('weighted_share_value'))['val']

            annotated_shares\
                .annotate(relative_value=models.F('weighted_share_value') / models.Value(total_value, output_field=models.FloatField()))\
                .update(
                    estimated_share_total=models.Value(estimated_total_after_tax) * models.F('relative_value'),
                    actual_share_total=models.Value(actual_total_after_tax) * models.F('relative_value'),
                )


def add_totals(apps, schema_editor):
    Entry = apps.get_model('allianceauth_pve.Entry')
    EntryRole = apps.get_model('allianceauth_pve.EntryRole')

    for entry in Entry.objects.all():
        update_share_totals_legacy(entry, EntryRole)


class Migration(migrations.Migration):

    dependencies = [
        ('allianceauth_pve', '0015_alter_entry_estimated_total_alter_pvebutton_amount_and_more'),
    ]

    operations = [
        migrations.RunPython(migrations.RunPython.noop, add_totals),
        migrations.RemoveField(
            model_name='entrycharacter',
            name='actual_share_total',
        ),
        migrations.RemoveField(
            model_name='entrycharacter',
            name='estimated_share_total',
        ),
    ]
