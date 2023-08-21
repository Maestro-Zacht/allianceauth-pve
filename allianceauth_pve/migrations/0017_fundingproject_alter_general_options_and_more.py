# Generated by Django 4.0.10 on 2023-07-26 21:08

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('allianceauth_pve', '0016_remove_entrycharacter_actual_share_total_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FundingProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('goal', models.PositiveBigIntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.AlterModelOptions(
            name='general',
            options={'default_permissions': (), 'managed': False, 'permissions': (('access_pve', 'Access PvE: Can access pve pages and be added in entries'), ('manage_entries', 'Manage Entries: Can do CRUD operations with entries'), ('manage_rotations', 'Manage Rotations: Can do CRUD operations with rotations'), ('manage_funding_projects', 'Manage Funding Projects: Can do CRUD operations with funding projects'))},
        ),
        migrations.RemoveField(
            model_name='rotation',
            name='is_paid_out',
        ),
        migrations.AddField(
            model_name='entry',
            name='funding_percentage',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='entry',
            name='funding_project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='entries', to='allianceauth_pve.fundingproject'),
        ),
    ]
