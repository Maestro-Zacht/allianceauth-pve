from django.db.models import QuerySet, Sum, Manager, Count, F, Subquery, OuterRef
from django.db.models.functions import Coalesce


class EntryCharacterQuerySet(QuerySet):
    pass
    # def get_summary(self):
    # daily_query = self.values('character', 'entry__created_at__date').order_by()\
    #     .alias(share_count=Count('entry__shares'))\
    #     .filter(share_count__gte=F('entry__rotation__min_people_share_setup'))\
    #     .annotate(daily_setups=Count(Case(When(helped_setup=True, then=1), default=0)))\
    #     .annotate(valid_setups=Case(
    #         When(daily_setups__lte=F('entry__rotation__max_daily_setups'), then=F('daily_setups')),
    #         default=F('entry__rotation__max_daily_setups')
    #     ))

    # total_setups = daily_query.values('character', 'valid_setups').annotate(total_setups=Sum('valid_setups'))

    # total_setups = self.raw("""SELECT MAESTROENTRYCHARACTER.`character_id`, SUM(valid_setups) as total_setups
    #                         FROM (%s) as MAESTROSUBQ, `ratting_entrycharacter` MAESTROENTRYCHARACTER
    #                         WHERE MAESTROENTRYCHARACTER.`character_id` = MAESTROSUBQ.`character_id`
    #                         GROUP BY MAESTROENTRYCHARACTER.`character_id`
    #                         """,
    #                         params=daily_query.query
    #                         )

    # setup_query = self.filter(character=OuterRef('character')).values('character')\
    #     .alias(share_count=Count('entry__shares'))\
    #     .filter(share_count__gte=F('entry__rotation__min_people_share_setup'), helped_setup=True)\
    #     .annotate(total_setups=Count('pk'))

    # return self.values('character').order_by()\
    #     .annotate(total_setups=Coalesce(Subquery(setup_query.values('total_setups')[:1]), 0))\
    #     .annotate(estimated_total=Sum('estimated_share_total'))\
    #     .annotate(actual_total=Sum('actual_share_total'))

    # return self.values('character').order_by()\
    #     .annotate(estimated_total=Sum('estimated_total'))\
    #     .annotate(actual_total=Sum('actual_total'))


class EntryCharacterManager(Manager):
    def get_queryset(self):
        return EntryCharacterQuerySet(self.model, using=self._db)

    # def get_summary(self):
    #     return self.get_queryset().get_summary()
