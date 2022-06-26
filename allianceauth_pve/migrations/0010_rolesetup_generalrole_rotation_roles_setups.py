# Generated by Django 4.0.5 on 2022-06-26 15:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('allianceauth_pve', '0009_pvebutton_rotation_entry_buttons'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleSetup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='GeneralRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('value', models.PositiveIntegerField(help_text="Relative role value. Share values are computed using this field. If there are 2 roles with 10 and 15, they'll receive 10/25 and 15/25 of the share value.", verbose_name='relative role value')),
                ('setup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='allianceauth_pve.rolesetup')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.AddField(
            model_name='rotation',
            name='roles_setups',
            field=models.ManyToManyField(help_text='Setup avaiable for loading in the Entry form.', related_name='+', to='allianceauth_pve.rolesetup'),
        ),
    ]