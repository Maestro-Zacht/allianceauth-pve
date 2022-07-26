from django.db.models import Sum, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import EntryCharacter, Rotation


def running_averages(user, start_date, end_date=timezone.now()):
    rotations = Rotation.objects.filter(closed_at__range=(start_date, end_date)).get_setup_summary().filter(user=user).values('total_setups')
    result = EntryCharacter.objects.filter(entry__rotation__closed_at__range=(start_date, end_date), user=user)\
        .values('user').order_by()\
        .annotate(helped_setups=Coalesce(Subquery(rotations[:1]), 0))\
        .annotate(estimated_total=Sum('estimated_share_total'))\
        .annotate(actual_total=Sum('actual_share_total'))\
        .values(
        'helped_setups',
        'estimated_total',
        'actual_total'
    )

    if result.exists():
        return result[0]
    else:
        return {}
