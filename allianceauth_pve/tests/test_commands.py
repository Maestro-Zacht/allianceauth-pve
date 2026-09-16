from io import StringIO

from django.core.cache import cache
from django.core.management import call_command

from allianceauth_pve.app_settings import (
    ACTIVITY_CACHE_KEY,
    FUNDING_PROJECT_SUMMARY_CACHE_KEY,
    ROTATION_PROJECT_SUMMARY_CACHE_KEY,
    ROTATION_SUMMARY_CACHE_KEY,
)
from allianceauth_pve.models import FundingProject

from .utils import PveTestBase


class TestPveClearCache(PveTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser, cls.testcharacter = cls.make_user(
            "aauth_testuser", 2116790529, "aauth_testchar"
        )

        cls.rotation = cls.make_rotation(name="test1rot")

        cls.funding_project = FundingProject.objects.create(
            name="testproject", goal=1_000_000_000
        )

        cls.make_entry(cls.rotation, cls.testuser, cls.testcharacter)

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
