from io import StringIO

from allianceauth.tests.auth_utils import AuthUtils
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase

from allianceauth_pve.app_settings import (
    ACTIVITY_CACHE_KEY,
    FUNDING_PROJECT_SUMMARY_CACHE_KEY,
    ROTATION_PROJECT_SUMMARY_CACHE_KEY,
    ROTATION_SUMMARY_CACHE_KEY,
)
from allianceauth_pve.models import (
    Entry,
    EntryCharacter,
    EntryRole,
    FundingProject,
    Rotation,
)


class TestPveClearCache(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user("aauth_testuser")
        cls.testcharacter = AuthUtils.add_main_character_2(
            cls.testuser, "aauth_testchar", 2116790529
        )

        cls.rotation = Rotation.objects.create(name="test1rot")

        cls.funding_project = FundingProject.objects.create(
            name="testproject", goal=1_000_000_000
        )

        entry = Entry.objects.create(
            rotation=cls.rotation,
            created_by=cls.testuser,
            estimated_total=1_000_000_000,
        )

        role = EntryRole.objects.create(entry=entry, name="testrole1", value=1)

        EntryCharacter.objects.create(
            entry=entry,
            user=cls.testuser,
            user_character=cls.testcharacter,
            role=role,
            site_count=1,
            helped_setup=False,
        )

    def test_clears_all_cache_keys(self):
        keys = [
            ROTATION_SUMMARY_CACHE_KEY.format(rotation_id=self.rotation.pk),
            ROTATION_PROJECT_SUMMARY_CACHE_KEY.format(rotation_id=self.rotation.pk),
            FUNDING_PROJECT_SUMMARY_CACHE_KEY.format(
                project_id=self.funding_project.pk
            ),
            *(
                ACTIVITY_CACHE_KEY.format(user_id=self.testuser.pk, months=months)
                for months in (1, 3, 6, 12)
            ),
        ]
        for key in keys:
            cache.set(key, "sentinel", 60)

        out = StringIO()
        call_command("pve_clear_cache", stdout=out)

        self.assertIn("Cache cleared!", out.getvalue())
        for key in keys:
            self.assertIsNone(cache.get(key))
