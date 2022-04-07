from django.db import models
from django.conf import settings
from django.utils import timezone


class Rotation(models.Model):
    name = models.CharField(max_length=128)

    actual_total = models.FloatField(default=0)

    tax_rate = models.FloatField(default=0)
    is_closed = models.BooleanField(default=False)
    is_paid_out = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    characters = models.ManyToManyField(settings.AUTH_USER_MODEL, through='RotationStats', related_name='rotations')

    priority = models.IntegerField(default=0)

    @property
    def days_since(self):
        return (timezone.now() - self.created_at).days

    @property
    def sales_percentage(self):
        rotation = self.entries.aggregate(estimated_total=models.Sum('estimated_total'))
        if not self.actual_total or not rotation['estimated_total']:
            return 0.00
        return self.actual_total / rotation['estimated_total']

    def __str__(self):
        return f'{self.pk} {self.name}'


class EntryCharacter(models.Model):
    share_count = models.PositiveIntegerField(default=1)
    entry = models.ForeignKey('Entry', on_delete=models.CASCADE, related_name='+')
    character = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    helped_setup = models.BooleanField(default=False)
    estimated_share_total = models.FloatField(default=0)
    actual_share_total = models.FloatField(default=0)

    @property
    def estimated_total(self):
        return (self.entry.estimated_total_after_tax / self.entry.total_shares_count) * self.share_count

    @property
    def actual_total(self):
        return (self.entry.actual_total_after_tax / self.entry.total_shares_count) * self.share_count

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['entry', 'character'], name='unique_character'),
        ]


class Entry(models.Model):
    rotation = models.ForeignKey('Rotation', on_delete=models.CASCADE, related_name='entries')
    shares = models.ManyToManyField(settings.AUTH_USER_MODEL, through=EntryCharacter)
    estimated_total = models.FloatField(default=0)
    total_shares_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'entry'
        verbose_name_plural = 'entries'

    @property
    def estimated_total_after_tax(self):
        tax_perc = (100 - self.rotation.tax_rate) / 100
        return self.estimated_total * tax_perc

    @property
    def actual_total_after_tax(self):
        return self.estimated_total_after_tax * self.rotation.sales_percentage

    def update_share_totals(self):
        self.total_shares_count = self.shares.aggregate(val=models.Sum('share_count'))["val"]
        if self.total_shares_count == 0 or self.total_shares_count is None:
            self.delete()
        else:
            self.save()

            self.ratting_shares\
                .annotate(estimated_total_after_tax=models.Value(self.estimated_total) * (models.Value(100) - models.Value(self.rotation.tax_rate)) / models.Value(100))\
                .annotate(actual_total_after_tax=models.F('estimated_total_after_tax') * models.Value(self.rotation.sales_percentage))\
                .update(
                    estimated_share_total=(models.F('estimated_total_after_tax') / models.Value(self.total_shares_count)) * models.F('share_count'),
                    actual_share_total=(models.F('actual_total_after_tax') / models.Value(self.total_shares_count)) * models.F('share_count')
                )


class RotationStats(models.Model):
    rotation = models.ForeignKey('Rotation', on_delete=models.CASCADE, related_name='summary')
    character = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rotations_stats')
    estimated_total = models.FloatField(default=0)
    actual_total = models.FloatField(default=0)
    helped_setup = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['rotation', 'character'], name='unique_char_stats'),
        ]
