from django.core.cache import cache
from django.utils import timezone

from allianceauth_pve.app_settings import ACTIVITY_CACHE_KEY
from allianceauth_pve.tests.utils import ACCESS, PveApiTestBase, url


class TestActivityApi(PveApiTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.user, cls.char = cls.make_user(
            "act_user", 90300001, "ActUser", perms=[ACCESS]
        )
        rotation = cls.make_rotation(
            name="actrot",
            is_closed=True,
            closed_at=timezone.now(),
            actual_total=900_000_000,
        )
        cls.make_entry(rotation, cls.user, cls.char, estimated_total=1_000_000_000)

    def test_get_activity_shape(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("get_activity", months=3))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(
            set(data), {"helped_setups", "estimated_total", "actual_total"}
        )
        self.assertGreater(data["estimated_total"], 0)

    def test_get_activity_invalid_months(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("get_activity", months=0))
        self.assertEqual(resp.status_code, 400)

    def test_get_activity_cached(self):
        self.client.force_login(self.user)
        first = self.client.get(url("get_activity", months=6))
        self.assertEqual(first.status_code, 200)
        cache_key = ACTIVITY_CACHE_KEY.format(user_id=self.user.pk, months=6)
        self.assertIsNotNone(cache.get(cache_key))
        second = self.client.get(url("get_activity", months=6))
        self.assertEqual(second.json(), first.json())
