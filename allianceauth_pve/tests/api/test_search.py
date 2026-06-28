from typing import TYPE_CHECKING
from unittest.mock import patch

from allianceauth.tests.auth_utils import AuthUtils
from django.contrib.auth.models import Group

from allianceauth_pve.tests.utils import ACCESS, MANAGE_ENTRIES, PveApiTestBase

if TYPE_CHECKING:
    from allianceauth.authentication.models import State


class TestSearchApi(PveApiTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.caller, _ = cls.make_user(
            "search_caller",
            90700000,
            "Caller",
            perms=[ACCESS, MANAGE_ENTRIES],
            ownership=False,
        )
        cls.ratter1, cls.ratter1_main = cls.make_user(
            "ratter1", 90700001, "AlphaMain", perms=[ACCESS]
        )
        cls.ratter1_alt = cls.add_alt(cls.ratter1, 90700002, "AlphaAlt")
        cls.ratter2, cls.ratter2_main = cls.make_user(
            "ratter2", 90700003, "BravoMain", perms=[ACCESS]
        )

    def _get_result_ids(self, resp):
        return {row["character"]["character_id"] for row in resp.json()}

    def test_search_ratters_basic(self):
        self.client.force_login(self.caller)
        resp = self.api_request("POST", "search_ratters", [])
        self.assertEqual(resp.status_code, 200)
        self.assertSetEqual(self._get_result_ids(resp), {90700001, 90700002, 90700003})

    def test_search_ratters_shape(self):
        self.client.force_login(self.caller)
        resp = self.api_request("POST", "search_ratters", [])
        main_row = next(
            r for r in resp.json() if r["character"]["character_id"] == 90700001
        )
        self.assertEqual(set(main_row), {"character", "main_character", "extra_chars"})
        self.assertEqual(main_row["main_character"]["character_id"], 90700001)
        self.assertIn("AlphaAlt", main_row["extra_chars"])

    def test_search_ratters_exclude_ids(self):
        self.client.force_login(self.caller)
        resp = self.api_request("POST", "search_ratters", [90700002])
        self.assertSetEqual(self._get_result_ids(resp), {90700001, 90700003})

    def test_search_ratters_name_main(self):
        self.client.force_login(self.caller)
        resp = self.api_request("POST", "search_ratters", [], query="?name=Bravo")
        self.assertSetEqual(self._get_result_ids(resp), {90700003})

    def test_search_ratters_name_alt(self):
        self.client.force_login(self.caller)
        resp = self.api_request("POST", "search_ratters", [], query="?name=AlphaAlt")
        self.assertSetEqual(self._get_result_ids(resp), {90700001, 90700002})

    @patch("allianceauth_pve.api.search.PVE_ONLY_MAINS", new=True)
    def test_search_ratters_only_mains(self):
        self.client.force_login(self.caller)
        resp = self.api_request("POST", "search_ratters", [])
        self.assertSetEqual(self._get_result_ids(resp), {90700001, 90700003})

    @patch("allianceauth_pve.api.search.PVE_ONLY_MAINS", new=True)
    def test_search_ratters_only_mains_name_alt(self):
        self.client.force_login(self.caller)
        resp = self.api_request("POST", "search_ratters", [], query="?name=AlphaAlt")
        self.assertSetEqual(self._get_result_ids(resp), {90700001})

    def test_search_ratters_permission_sources(self):
        group = Group.objects.create(name="pve_group")
        perm = AuthUtils.get_permission_by_name(ACCESS)
        AuthUtils.add_permissions_to_groups([perm], [group])
        group_user, _ = self.make_user("grp_user", 90700010, "GroupMain")
        group_user.groups.add(group)

        state: State = AuthUtils.create_state("PvEState", 500)
        state.permissions.add(perm)
        state_user, _ = self.make_user("state_user", 90700011, "StateMain")
        AuthUtils.assign_state(state_user, state, disconnect_signals=True)

        self.client.force_login(self.caller)
        resp = self.api_request("POST", "search_ratters", [])
        ids = self._get_result_ids(resp)
        self.assertIn(90700010, ids)
        self.assertIn(90700011, ids)

    # ---- search_items ----

    def test_search_items_success(self):
        self.make_item(34, "Tritanium", group_id=18)
        self.make_item(35, "Pyerite", group_id=18)
        self.client.force_login(self.caller)
        resp = self.api_request("POST", "search_items", "Tritanium 1.000\nPyerite 500")
        self.assertEqual(resp.status_code, 200, resp.content)
        data = {row["name"]: row for row in resp.json()}
        self.assertEqual(data["Tritanium"]["quantity"], 1000)
        self.assertEqual(data["Pyerite"]["quantity"], 500)
        self.assertFalse(data["Tritanium"]["is_ignored"])

    @patch("allianceauth_pve.api.search.PVE_IGNORED_ITEM_GROUPS", {880})
    def test_search_items_ignored_flag(self):
        self.make_item(99700080, "IgnoredItem", group_id=880)
        self.client.force_login(self.caller)
        resp = self.api_request("POST", "search_items", "IgnoredItem 5")
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertTrue(resp.json()[0]["is_ignored"])

    def test_search_items_unparseable(self):
        self.client.force_login(self.caller)
        resp = self.api_request("POST", "search_items", "invalidline")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("invalidline", resp.json())

    def test_search_items_missing_item(self):
        self.client.force_login(self.caller)
        resp = self.api_request("POST", "search_items", "Nonexistent Item 5")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Nonexistent Item", resp.json())
