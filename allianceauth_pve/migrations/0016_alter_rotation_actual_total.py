# Generated by Django 4.0.7 on 2022-10-05 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('allianceauth_pve', '0015_alter_entry_estimated_total_alter_pvebutton_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rotation',
            name='actual_total',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]