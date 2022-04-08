from django.db.models import Count

from .models import EntryCharacter, Rotation, Entry


class EntryService:
    @staticmethod
    def _update_stats_entry_create(entry, shares):
        EntryCharacter.objects.bulk_create([
            EntryCharacter(
                entry=entry,
                character_id=row.character_id,
                share_count=row.share_count,
                helped_setup=row.helped_setup
            ) for row in shares
        ])

        entry.update_share_totals()

        for share in entry.ratting_shares.all():
            char = share.character
            char_stats, _ = entry.rotation.summary.get_or_create(character=char)
            char_stats.estimated_total += share.estimated_share_total

            if entry.shares.count() > 2 and share.helped_setup:
                today_char_shares = EntryCharacter.objects.alias(entry_shares=Count('entry__ratting_shares')).filter(
                    character=char,
                    entry__created_at__date=entry.created_at.date(),
                    helped_setup=True,
                    entry_shares__gte=3
                )
                if today_char_shares.count() == 1:
                    char_stats.helped_setup += 1

            char_stats.save()

    @staticmethod
    def _update_stats_entry_delete(entry):
        for share in entry.ratting_shares.all():
            char_stats = entry.rotation.summary.get(character=share.character)

            char_stats.estimated_total -= share.estimated_share_total
            char_stats.actual_total -= share.actual_share_total

            day_shares = EntryCharacter.objects.alias(entry_shares=Count('entry__ratting_shares')).filter(
                character=share.character,
                entry__created_at__date=entry.created_at.date(),
                helped_setup=True,
                entry_shares__gte=3,
            )

            if day_shares.count() == 1 and entry.shares.count() > 2:
                char_stats.helped_setup -= 1

            char_stats.save()

    @staticmethod
    def create_entry(user, rotation_id, estimated_total, shares):
        rotation = Rotation.objects.get(pk=rotation_id)

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

        entry.estimated_total = estimated_total
        entry.save()

        EntryService._update_stats_entry_delete(entry)

        entry.ratting_shares.all().delete()

        EntryService._update_stats_entry_create(entry, shares)

        entry.rotation.summary.filter(estimated_total__lt=1).delete()

        return entry

    @staticmethod
    def delete_entry(user, entry_id) -> Rotation:
        entry = Entry.objects.get(pk=entry_id)

        if entry.rotation.is_closed:
            raise Exception('Rotation is closed and can not be modified')

        EntryService._update_stats_entry_delete(entry)

        rotation = entry.rotation

        entry.delete()

        rotation.summary.filter(estimated_total__lt=1).delete()

        return rotation
