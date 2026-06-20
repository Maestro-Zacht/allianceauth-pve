from django.core.cache import cache
from django.core.management.base import BaseCommand

from allianceauth_pve.app_settings import (
    ACTIVITY_CACHE_KEY,
    FUNDING_PROJECT_SUMMARY_CACHE_KEY,
    ROTATION_PROJECT_SUMMARY_CACHE_KEY,
    ROTATION_SUMMARY_CACHE_KEY,
)
from allianceauth_pve.models import EntryCharacter, FundingProject, Rotation


class Command(BaseCommand):
    help = "Clears Redis cache for the PvE app"

    def handle(self, *args, **options):  # noqa: ARG002
        self.stdout.write("Clearing PvE cache...")
        cache.delete_many(
            ROTATION_SUMMARY_CACHE_KEY.format(rotation_id=rotation_id)
            for rotation_id in Rotation.objects.values_list("pk", flat=True)
        )
        cache.delete_many(
            ROTATION_PROJECT_SUMMARY_CACHE_KEY.format(rotation_id=rotation_id)
            for rotation_id in Rotation.objects.values_list("pk", flat=True)
        )
        cache.delete_many(
            FUNDING_PROJECT_SUMMARY_CACHE_KEY.format(project_id=project_id)
            for project_id in FundingProject.objects.values_list("pk", flat=True)
        )
        cache.delete_many(
            ACTIVITY_CACHE_KEY.format(user_id=user_id, months=months)
            for user_id in EntryCharacter.objects.values_list(
                "user_id", flat=True
            ).distinct()
            for months in [1, 3, 6, 12]
        )
        self.stdout.write(self.style.SUCCESS("Cache cleared!"))
