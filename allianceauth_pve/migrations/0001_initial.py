# Generated by Django 3.2.12 on 2022-04-08 18:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0019_merge_20211026_0919'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estimated_total', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'entry',
                'verbose_name_plural': 'entries',
            },
        ),
        migrations.CreateModel(
            name='Rotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('actual_total', models.FloatField(default=0)),
                ('max_daily_setups', models.PositiveSmallIntegerField(default=1, help_text='The maximum number of helped setup per day. If more are submitted, only this number is counted. 0 for deactivating helped setups.')),
                ('min_people_share_setup', models.PositiveSmallIntegerField(default=3, help_text='The minimum number of people in an entry to consider the helped setup valid.')),
                ('tax_rate', models.FloatField(default=0)),
                ('is_closed', models.BooleanField(default=False)),
                ('is_paid_out', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('priority', models.IntegerField(default=0, help_text='Ordering priority. The higher priorities are in the first positions.')),
                ('accessible_to_states', models.ManyToManyField(help_text='People in the selected states will be able to see the rotation.', related_name='_allianceauth_pve_rotation_accessible_to_states_+', to='authentication.State')),
                ('accessible_to_users', models.ManyToManyField(help_text='Selected people will be able to see the rotation.', related_name='_allianceauth_pve_rotation_accessible_to_users_+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RotationStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estimated_total', models.FloatField(default=0)),
                ('actual_total', models.FloatField(default=0)),
                ('helped_setup', models.IntegerField(default=0)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rotations_stats', to=settings.AUTH_USER_MODEL)),
                ('rotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='summary', to='allianceauth_pve.rotation')),
            ],
        ),
        migrations.AddField(
            model_name='rotation',
            name='partecipants',
            field=models.ManyToManyField(related_name='rotations', through='allianceauth_pve.RotationStats', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='EntryCharacter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('share_count', models.PositiveIntegerField(default=1)),
                ('helped_setup', models.BooleanField(default=False)),
                ('estimated_share_total', models.FloatField(default=0)),
                ('actual_share_total', models.FloatField(default=0)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratting_shares', to=settings.AUTH_USER_MODEL)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratting_shares', to='allianceauth_pve.entry')),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='rotation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='allianceauth_pve.rotation'),
        ),
        migrations.AddField(
            model_name='entry',
            name='shares',
            field=models.ManyToManyField(related_name='_allianceauth_pve_entry_shares_+', through='allianceauth_pve.EntryCharacter', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='rotationstats',
            constraint=models.UniqueConstraint(fields=('rotation', 'character'), name='unique_char_stats'),
        ),
        migrations.AddConstraint(
            model_name='entrycharacter',
            constraint=models.UniqueConstraint(fields=('entry', 'character'), name='unique_character'),
        ),
    ]
