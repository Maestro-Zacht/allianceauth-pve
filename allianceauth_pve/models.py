from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.functions import Coalesce

from allianceauth.services.hooks import get_extension_logger
from allianceauth.eveonline.models import EveCharacter

logger = get_extension_logger(__name__)


class General(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("access_pve", "Can access pve pages and be added in entries"),
            ('manage_entries', "Can do CRUD operations with entries"),
            ("manage_rotations", "Can do CRUD operations with rotations"),
        )


class RotationQueryset(models.QuerySet):
    def get_setup_summary(self):
        return RotationSetupSummary.objects.filter(rotation__in=self).order_by().values('user')\
            .annotate(total_setups=Coalesce(models.Sum('valid_setups'), 0))\



class RotationManager(models.Manager):
    def get_queryset(self):
        return RotationQueryset(self.model, using=self._db)

    def get_setup_summary(self):
        return self.get_queryset().get_setup_summary()


class Rotation(models.Model):
    name = models.CharField(max_length=128)

    actual_total = models.FloatField(default=0)

    max_daily_setups = models.PositiveSmallIntegerField(default=1, help_text='The maximum number of helped setup per day. If more are submitted, only this number is counted. 0 for deactivating helped setups.')
    min_people_share_setup = models.PositiveSmallIntegerField(default=3, help_text='The minimum number of people in an entry to consider the helped setup valid.')

    tax_rate = models.FloatField(default=0, help_text='Tax rate in percentage')
    is_closed = models.BooleanField(default=False)
    is_paid_out = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    priority = models.IntegerField(default=0, help_text='Ordering priority. The higher priorities are in the first positions.')

    objects = RotationManager()

    @property
    def summary(self):
        setup_summary = Rotation.objects.filter(pk=self.pk).get_setup_summary().filter(user_id=models.OuterRef('user_id')).values('total_setups')
        return EntryCharacter.objects.filter(entry__rotation=self).values('user').order_by()\
            .annotate(helped_setups=Coalesce(models.Subquery(setup_summary[:1]), 0))\
            .annotate(estimated_total=models.Sum('estimated_share_total'))\
            .annotate(actual_total=models.Sum('actual_share_total'))

    @property
    def days_since(self):
        return (timezone.now() - self.created_at).days

    @property
    def sales_percentage(self):
        estimated = self.estimated_total
        return 0.00 if not self.actual_total or estimated == 0 else self.actual_total / estimated

    @property
    def estimated_total(self):
        return self.entries.aggregate(estimated_total=Coalesce(models.Sum('estimated_total'), 0.0))['estimated_total']

    def __str__(self):
        return f'{self.pk} {self.name}'

    class Meta:
        default_permissions = ()


class EntryCharacter(models.Model):
    entry = models.ForeignKey('Entry', on_delete=models.CASCADE, related_name='ratting_shares')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratting_shares')
    user_character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE, related_name='ratting_shares')
    role = models.ForeignKey('EntryRole', on_delete=models.RESTRICT, related_name='shares')

    site_count = models.PositiveIntegerField(default=1)
    helped_setup = models.BooleanField(default=False)
    estimated_share_total = models.FloatField(default=0)
    actual_share_total = models.FloatField(default=0)

    class Meta:
        default_permissions = ()


class Entry(models.Model):
    rotation = models.ForeignKey(Rotation, on_delete=models.CASCADE, related_name='entries')
    estimated_total = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'entry'
        verbose_name_plural = 'entries'

    @property
    def total_shares_count(self):
        return self.ratting_shares.aggregate(val=models.Count('user_id', distinct=True))['val']

    @property
    def estimated_total_after_tax(self):
        tax_perc = (100 - self.rotation.tax_rate) / 100
        return self.estimated_total * tax_perc

    @property
    def actual_total_after_tax(self):
        return self.estimated_total_after_tax * self.rotation.sales_percentage

    def update_share_totals(self):
        sum_sites = self.ratting_shares.aggregate(val=Coalesce(models.Sum('site_count'), 0))['val']

        self.roles.alias(char_count=models.Count('shares')).filter(char_count=0).delete()
        num_roles = self.roles.count()
        if sum_sites == 0 or num_roles == 0:
            self.delete()
        else:
            self.save()

            estimated_total_after_tax = self.estimated_total * (100 - self.rotation.tax_rate) / 100
            actual_total_after_tax = estimated_total_after_tax * self.rotation.sales_percentage

            if settings.DATABASES[self.ratting_shares.db]['ENGINE'] == 'django.db.backends.mysql':
                total_value = 0
                for role in self.roles.all():
                    total_value += role.shares.annotate(weighted_share_value=models.F('site_count') * models.Value(role.value))\
                        .aggregate(val=models.Sum('weighted_share_value'))['val']

                for role in self.roles.all():
                    role.shares\
                        .annotate(weighted_share_value=models.F('site_count') * models.Value(role.value))\
                        .annotate(relative_value=models.F('weighted_share_value') / models.Value(total_value, output_field=models.FloatField()))\
                        .update(
                            estimated_share_total=models.Value(estimated_total_after_tax) * models.F('relative_value'),
                            actual_share_total=models.Value(actual_total_after_tax) * models.F('relative_value'),
                        )
            else:
                role_val_query = EntryRole.objects.filter(pk=models.OuterRef('role_id')).values('value')

                annotated_shares = self.ratting_shares\
                    .annotate(role_val=models.Subquery(role_val_query))\
                    .annotate(weighted_share_value=models.F('site_count') * models.F('role_val'))

                total_value = annotated_shares.aggregate(val=models.Sum('weighted_share_value'))['val']

                annotated_shares\
                    .annotate(relative_value=models.F('weighted_share_value') / models.Value(total_value, output_field=models.FloatField()))\
                    .update(
                        estimated_share_total=models.Value(estimated_total_after_tax) * models.F('relative_value'),
                        actual_share_total=models.Value(actual_total_after_tax) * models.F('relative_value'),
                    )

    class Meta:
        default_permissions = ()


class EntryRole(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='roles')

    name = models.CharField(max_length=64)
    value = models.PositiveIntegerField('relative role value', help_text="Relative role value. Share values are computed using this field. If there are 2 roles with 10 and 15, they'll receive 10/25 and 15/25 of the share value.")

    def __str__(self) -> str:
        return self.name

    @property
    def approximate_percentage(self):
        return self.value * 100 / self.entry.roles.aggregate(val=models.Sum('value'))['val']

    class Meta:
        default_permissions = ()


class RotationSetupSummary(models.Model):
    id = models.BigIntegerField(primary_key=True)
    rotation = models.ForeignKey(Rotation, on_delete=models.DO_NOTHING, related_name='+')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='rotations_stats')
    entry_date = models.DateField()
    valid_setups = models.IntegerField()

    class Meta:
        managed = False  # this is a view, check 0003 and 0005
        db_table = 'allianceauth_pve_setup_summary'
        default_permissions = ()
