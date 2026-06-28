from unittest import mock

from django.core.cache import cache

from allianceauth_pve.app_settings import (
    ROTATION_PROJECT_SUMMARY_CACHE_KEY,
    ROTATION_SUMMARY_CACHE_KEY,
)
from allianceauth_pve.models import (
    EntryLootItem,
    FundingProject,
    GeneralRole,
    PveButton,
    RoleSetup,
    Rotation,
)
from allianceauth_pve.tests.utils import (
    ACCESS,
    MANAGE_ENTRIES,
    MANAGE_ROTATIONS,
    PveApiTestBase,
    url,
)


class TestRotationsApi(PveApiTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.user, cls.char = cls.make_user(
            "rot_user",
            90400001,
            "RotUser",
            perms=[ACCESS, MANAGE_ROTATIONS, MANAGE_ENTRIES],
        )
        cls.rotation = cls.make_rotation(name="existing", tax_rate=10.0)
        cls.entry, cls.role, cls.share = cls.make_entry(
            cls.rotation, cls.user, cls.char
        )
        cls.button = PveButton.objects.create(text="rbtn", amount=5)
        cls.setup = RoleSetup.objects.create(name="rsetup")
        GeneralRole.objects.create(setup=cls.setup, name="dps", value=10)

    # ---- list / get ----

    def test_list_rotations(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("list_rotations"))
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], self.rotation.pk)

    def test_get_rotation(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("get_rotation", rotation_id=self.rotation.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], self.rotation.pk)

    def test_get_rotation_404(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("get_rotation", rotation_id=999999))
        self.assertEqual(resp.status_code, 404)

    # ---- create ----

    def test_create_rotation_success(self):
        self.client.force_login(self.user)
        payload = self.rotation_payload(
            name="Created", entry_buttons=[self.button.pk], roles_setups=[self.setup.pk]
        )
        resp = self.api_request("POST", "create_rotation", payload)
        self.assertEqual(resp.status_code, 200, resp.content)
        rotation = Rotation.objects.get(pk=resp.json())
        self.assertEqual(rotation.name, "Created")
        self.assertQuerySetEqual(rotation.entry_buttons.all(), [self.button])
        self.assertQuerySetEqual(rotation.roles_setups.all(), [self.setup])

    def test_create_rotation_empty_name(self):
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "create_rotation", self.rotation_payload(name="")
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("name", resp.json())

    def test_create_rotation_long_name(self):
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "create_rotation", self.rotation_payload(name="x" * 129)
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("name", resp.json())

    def test_create_rotation_bad_tax_rate(self):
        self.client.force_login(self.user)
        for value in (-1.0, 101.0):
            with self.subTest(tax_rate=value):
                resp = self.api_request(
                    "POST", "create_rotation", self.rotation_payload(tax_rate=value)
                )
                self.assertEqual(resp.status_code, 400)
                self.assertIn("tax_rate", resp.json())

    def test_create_rotation_negative_daily_setups(self):
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "create_rotation", self.rotation_payload(max_daily_setups=-1)
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("max_daily_setups", resp.json())

    def test_create_rotation_negative_min_people(self):
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "create_rotation", self.rotation_payload(min_people_share_setup=-1)
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("min_people_share_setup", resp.json())

    def test_create_rotation_invalid_buttons(self):
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "create_rotation", self.rotation_payload(entry_buttons=[999999])
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("entry_buttons", resp.json())

    def test_create_rotation_invalid_roles_setups(self):
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "create_rotation", self.rotation_payload(roles_setups=[999999])
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("roles_setups", resp.json())

    # ---- close ----

    def test_close_rotation_success(self):
        rotation = self.make_rotation(name="toclose")
        self.client.force_login(self.user)
        resp = self.api_request(
            "PATCH",
            "close_rotation",
            {"sales_value": 500_000_000, "item_sales": []},
            rotation_id=rotation.pk,
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        rotation.refresh_from_db()
        self.assertTrue(rotation.is_closed)
        self.assertEqual(rotation.actual_total, 500_000_000)
        self.assertIsNotNone(rotation.closed_at)

    def test_close_rotation_with_item_sales(self):
        rotation = self.make_rotation(name="closeitems")
        entry, _, _ = self.make_entry(rotation, self.user, self.char)
        item = self.make_item(99400001, "Loot A")
        self.make_loot_item(entry, item, quantity=10)

        self.client.force_login(self.user)
        resp = self.api_request(
            "PATCH",
            "close_rotation",
            {
                "sales_value": 100_000_000,
                "item_sales": [{"item_id": item.id, "sale_value": 50_000_000}],
            },
            rotation_id=rotation.pk,
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        loot = EntryLootItem.objects.get(entry=entry, item=item)
        self.assertAlmostEqual(loot.sale_price, 50_000_000 / 10)

    def test_close_rotation_negative_sales(self):
        rotation = self.make_rotation(name="negsales")
        self.client.force_login(self.user)
        resp = self.api_request(
            "PATCH",
            "close_rotation",
            {"sales_value": -1, "item_sales": []},
            rotation_id=rotation.pk,
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("sales_value", data)
        self.assertGreater(len(data["sales_value"]), 0)

    def test_close_rotation_duplicate_item(self):
        rotation = self.make_rotation(name="dupitem")
        entry, _, _ = self.make_entry(rotation, self.user, self.char)
        item = self.make_item(99400003, "Dup")
        self.make_loot_item(entry, item, quantity=2)

        self.client.force_login(self.user)
        resp = self.api_request(
            "PATCH",
            "close_rotation",
            {
                "sales_value": 0,
                "item_sales": [
                    {"item_id": item.id, "sale_value": 100},
                    {"item_id": item.id, "sale_value": 200},
                ],
            },
            rotation_id=rotation.pk,
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("item_sales", data)
        self.assertIn("1", data["item_sales"])

    def test_close_rotation_items_missing(self):
        rotation = self.make_rotation(name="missingitems")
        entry, _, _ = self.make_entry(rotation, self.user, self.char)
        item = self.make_item(99400004, "Missing")
        self.make_loot_item(entry, item, quantity=2)

        self.client.force_login(self.user)
        resp = self.api_request(
            "PATCH",
            "close_rotation",
            {"sales_value": 0, "item_sales": []},
            rotation_id=rotation.pk,
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("items_missing", data)
        self.assertListEqual(data["items_missing"], [item.id])

    def test_close_rotation_already_closed(self):
        rotation = self.make_rotation(name="closed", is_closed=True)
        self.client.force_login(self.user)
        resp = self.api_request(
            "PATCH",
            "close_rotation",
            {"sales_value": 1, "item_sales": []},
            rotation_id=rotation.pk,
        )
        self.assertEqual(resp.status_code, 403)

    def test_close_rotation_404(self):
        self.client.force_login(self.user)
        resp = self.api_request(
            "PATCH",
            "close_rotation",
            {"sales_value": 1, "item_sales": []},
            rotation_id=999999,
        )
        self.assertEqual(resp.status_code, 404)

    # ---- rotation sub-resources ----

    def test_get_rotation_summary(self):
        self.client.force_login(self.user)
        target = url("get_rotation_summary", rotation_id=self.rotation.pk)
        resp = self.client.get(target)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["character_id"], self.char.character_id)

        cache_key = ROTATION_SUMMARY_CACHE_KEY.format(rotation_id=self.rotation.pk)
        self.assertTrue(cache.has_key(cache_key))
        with mock.patch.object(cache, "get", wraps=cache.get) as mock_cache_get:
            resp2 = self.client.get(target)
            self.assertEqual(resp2.status_code, 200)
            self.assertEqual(resp2.json(), data)
            mock_cache_get.assert_called_with(cache_key)

    def test_get_rotation_summary_404(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("get_rotation_summary", rotation_id=999999))
        self.assertEqual(resp.status_code, 404)

    def test_get_rotation_project_summaries(self):
        project = FundingProject.objects.create(name="rotproj", goal=1_000_000)
        rotation = self.make_rotation(name="withproj")
        self.make_entry(
            rotation,
            self.user,
            self.char,
            funding_project=project,
            funding_percentage=50,
        )
        self.client.force_login(self.user)
        resp = self.client.get(
            url("get_rotation_project_summaries", rotation_id=rotation.pk)
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["project"]["id"], project.pk)
        cache_key = ROTATION_PROJECT_SUMMARY_CACHE_KEY.format(rotation_id=rotation.pk)
        self.assertTrue(cache.has_key(cache_key))

        with mock.patch.object(cache, "get", wraps=cache.get) as mock_cache_get:
            resp2 = self.client.get(
                url("get_rotation_project_summaries", rotation_id=rotation.pk)
            )
            self.assertEqual(resp2.status_code, 200)
            self.assertEqual(resp2.json(), data)

            mock_cache_get.assert_called_with(cache_key)

    def test_get_rotation_project_summaries_404(self):
        self.client.force_login(self.user)
        resp = self.client.get(
            url("get_rotation_project_summaries", rotation_id=999999)
        )
        self.assertEqual(resp.status_code, 404)

    def test_get_rotation_role_setups(self):
        self.rotation.roles_setups.add(self.setup)
        self.client.force_login(self.user)
        resp = self.client.get(
            url("get_rotation_role_setups", rotation_id=self.rotation.pk)
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "rsetup")
        self.assertEqual(data[0]["roles"][0]["name"], "dps")

    def test_get_rotation_role_setups_404(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("get_rotation_role_setups", rotation_id=999999))
        self.assertEqual(resp.status_code, 404)

    def test_get_rotation_buttons(self):
        self.rotation.entry_buttons.add(self.button)
        self.client.force_login(self.user)
        resp = self.client.get(
            url("get_rotation_buttons", rotation_id=self.rotation.pk)
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["text"], "rbtn")

    def test_get_rotation_buttons_404(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("get_rotation_buttons", rotation_id=999999))
        self.assertEqual(resp.status_code, 404)

    def test_get_rotation_items(self):
        item = self.make_item(99400010, "RotItem")
        self.make_loot_item(self.entry, item, quantity=7, sale_price=1000.0)
        self.client.force_login(self.user)
        resp = self.client.get(url("get_rotation_items", rotation_id=self.rotation.pk))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], item.id)
        self.assertEqual(data[0]["quantity"], 7)

    def test_get_rotation_items_404(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("get_rotation_items", rotation_id=999999))
        self.assertEqual(resp.status_code, 404)
