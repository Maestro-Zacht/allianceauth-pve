from django.db.models import Sum, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import EntryCharacter, Rotation, Entry


class EntryService:
    @staticmethod
    def _update_stats_entry_create(entry, shares):
        EntryCharacter.objects.bulk_create([
            EntryCharacter(
                entry=entry,
                user_id=row.user_id,
                share_count=row.share_count,
                helped_setup=row.helped_setup
            ) for row in shares
        ])

        entry.update_share_totals()

    @staticmethod
    def create_entry(user, rotation_id, estimated_total, shares):
        rotation = Rotation.objects.get(pk=rotation_id)

        if rotation.is_closed:
            return Exception('Rotation is closed')

        if estimated_total < 0 or estimated_total > 1000000000000:
            raise Exception('Total not valid')

        entry = Entry.objects.create(
            rotation=rotation,
            estimated_total=estimated_total,
            created_by=user,
        )

        EntryService._update_stats_entry_create(entry, shares)

        return entry

    @staticmethod
    def edit_entry(user, entry_id, estimated_total, shares):
        if estimated_total < 0 or estimated_total > 1000000000000:
            raise Exception('Total not valid')

        entry: Entry = Entry.objects.get(pk=entry_id)

        if entry.rotation.is_closed:
            return Exception('Rotation is closed')

        entry.estimated_total = estimated_total
        entry.save()

        entry.ratting_shares.all().delete()

        EntryService._update_stats_entry_create(entry, shares)

        return entry

    @staticmethod
    def delete_entry(user, entry_id) -> Rotation:
        entry = Entry.objects.get(pk=entry_id)

        if entry.rotation.is_closed:
            raise Exception('Rotation is closed and can not be modified')

        rotation = entry.rotation

        entry.delete()

        return rotation


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
