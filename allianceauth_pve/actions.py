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
