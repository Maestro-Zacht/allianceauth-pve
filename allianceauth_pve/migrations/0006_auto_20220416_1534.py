# Generated by Django 3.2.12 on 2022-04-16 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('allianceauth_pve', '0005_rename_character_entrycharacter_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='General',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('access_pve', 'Can access pve pages and be added in entries'), ('manage_entries', 'Can do CRUD operations with entries'), ('manage_rotations', 'Can do CRUD operations with rotations')),
                'managed': False,
                'default_permissions': (),
            },
        ),
        migrations.AlterModelOptions(
            name='entry',
            options={'default_permissions': ()},
        ),
        migrations.AlterModelOptions(
            name='entrycharacter',
            options={'default_permissions': ()},
        ),
        migrations.AlterModelOptions(
            name='rotation',
            options={'default_permissions': ()},
        ),
        migrations.AlterModelOptions(
            name='rotationsetupsummary',
            options={'default_permissions': (), 'managed': False},
        ),
    ]