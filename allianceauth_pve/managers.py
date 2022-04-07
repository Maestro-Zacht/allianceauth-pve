from django.db.models import QuerySet, Sum, Manager, When, Case, Count


class EntryCharacterQuerySet(QuerySet):
    def get_summary(self):
        return self.values('character').order_by()\
            .annotate(helped_setups=Count(Case(When(helped_setup=True, then=1), default=0)))\
            .annotate(estimated_total=Sum('estimated_total'))\
            .annotate(actual_total=Sum('actual_total'))


class EntryCharacterManager(Manager):
    def get_queryset(self):
        return EntryCharacterQuerySet(self.model, using=self._db)

    def get_summary(self):
        return self.get_queryset().get_summary()
