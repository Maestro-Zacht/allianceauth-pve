# Generated by Django 4.0.10 on 2023-07-31 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('allianceauth_pve', '0018_fundingproject_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundingproject',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]