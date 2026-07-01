from unittest.mock import patch

from allianceauth.eveonline.models import EveCharacter
from allianceauth.tests.auth_utils import AuthUtils

from allianceauth_pve.models import (
    Entry,
    EntryCharacter,
    FundingProject,
)
from allianceauth_pve.tests.utils import (
    ACCESS,
    MANAGE_ENTRIES,
    PveApiTestBase,
    url,
)


class TestEntriesApi(PveApiTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.owner, cls.owner_char = cls.make_user(
            "ent_owner", 90500001, "EntOwner", perms=[ACCESS, MANAGE_ENTRIES]
        )
        cls.other, cls.other_char = cls.make_user(
            "ent_other", 90500002, "EntOther", perms=[ACCESS, MANAGE_ENTRIES]
        )
        cls.superuser, cls.super_char = cls.make_superuser(
            "ent_super", 90500003, "EntSuper"
        )
        cls.access_only, cls.access_char = cls.make_user(
            "ent_access", 90500004, "EntAccess", perms=[ACCESS]
        )

        cls.rotation = cls.make_rotation(name="entrot", tax_rate=10.0)
        cls.entry, cls.role, cls.share = cls.make_entry(
            cls.rotation, cls.owner, cls.owner_char
        )
        cls.item = cls.make_item(99500001, "EntryItem")

    # ---- reads ----

    def test_get_rotation_entries(self):
        self.client.force_login(self.access_only)
        resp = self.client.get(
            url("get_rotation_entries", rotation_id=self.rotation.pk)
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.entry.pk)

    def test_get_rotation_entries_404(self):
        self.client.force_login(self.access_only)
        resp = self.client.get(url("get_rotation_entries", rotation_id=999999))
        self.assertEqual(resp.status_code, 404)

    def test_get_rotation_entry_user_can_edit(self):
        target = url(
            "get_rotation_entry", rotation_id=self.rotation.pk, entry_id=self.entry.pk
        )

        self.client.force_login(self.owner)
        self.assertTrue(self.client.get(target).json()["user_can_edit"])

        self.client.force_login(self.superuser)
        self.assertTrue(self.client.get(target).json()["user_can_edit"])

        self.client.force_login(self.access_only)
        resp = self.client.get(target)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()["user_can_edit"])

    def test_get_rotation_entry_404(self):
        self.client.force_login(self.owner)
        resp = self.client.get(
            url("get_rotation_entry", rotation_id=self.rotation.pk, entry_id=999999)
        )
        self.assertEqual(resp.status_code, 404)

    def test_get_rotation_entry_roles(self):
        self.client.force_login(self.access_only)
        resp = self.client.get(
            url(
                "get_rotation_entry_roles",
                rotation_id=self.rotation.pk,
                entry_id=self.entry.pk,
            )
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertAlmostEqual(data[0]["role_approximate_percentage"], 100.0)

    def test_get_rotation_entry_roles_404(self):
        self.client.force_login(self.access_only)
        resp = self.client.get(
            url(
                "get_rotation_entry_roles",
                rotation_id=self.rotation.pk,
                entry_id=999999,
            )
        )
        self.assertEqual(resp.status_code, 404)

    def test_get_rotation_entry_shares(self):
        self.client.force_login(self.access_only)
        resp = self.client.get(
            url(
                "get_rotation_entry_shares",
                rotation_id=self.rotation.pk,
                entry_id=self.entry.pk,
            )
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["role_name"], "dps")

    def test_get_rotation_entry_shares_404(self):
        self.client.force_login(self.access_only)
        resp = self.client.get(
            url(
                "get_rotation_entry_shares",
                rotation_id=self.rotation.pk,
                entry_id=999999,
            )
        )
        self.assertEqual(resp.status_code, 404)

    def test_get_rotation_entry_items(self):
        self.make_loot_item(self.entry, self.item, quantity=3, sale_price=10.0)
        self.client.force_login(self.access_only)
        resp = self.client.get(
            url(
                "get_rotation_entry_items",
                rotation_id=self.rotation.pk,
                entry_id=self.entry.pk,
            )
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.item.id)
        self.assertEqual(data[0]["quantity"], 3)

    def test_get_rotation_entry_items_404(self):
        self.client.force_login(self.access_only)
        resp = self.client.get(
            url(
                "get_rotation_entry_items",
                rotation_id=self.rotation.pk,
                entry_id=999999,
            )
        )
        self.assertEqual(resp.status_code, 404)

    # ---- new_entry ----

    def test_new_entry_success(self):
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id,
            shares=[
                {
                    "character_id": self.owner_char.character_id,
                    "helped_setup": True,
                    "site_count": 2,
                    "role_name": "dps",
                }
            ],
            items=[{"id": self.item.id, "quantity": 5}],
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 200, resp.content)

        new = Entry.objects.exclude(pk=self.entry.pk).get(rotation=self.rotation)
        self.assertEqual(new.roles.count(), 1)
        self.assertEqual(new.ratting_shares.count(), 1)
        self.assertEqual(new.loot_items.count(), 1)
        share = new.ratting_shares.get()
        self.assertTrue(share.helped_setup)
        self.assertEqual(share.site_count, 2)

    def test_new_entry_closed_rotation(self):
        rotation = self.make_rotation(name="closednew", is_closed=True)
        self.client.force_login(self.owner)
        resp = self.api_request(
            "POST",
            "new_entry",
            self.valid_entry_payload(self.owner_char.character_id),
            rotation_id=rotation.pk,
        )
        self.assertEqual(resp.status_code, 403)

    def test_new_entry_404(self):
        self.client.force_login(self.owner)
        resp = self.api_request(
            "POST",
            "new_entry",
            self.valid_entry_payload(self.owner_char.character_id),
            rotation_id=999999,
        )
        self.assertEqual(resp.status_code, 404)

    def test_new_entry_no_roles(self):
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(self.owner_char.character_id, roles=[])
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(resp.json()["roles_root"])

    def test_new_entry_duplicate_role_name(self):
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id,
            roles=[{"name": "dps", "value": 10}, {"name": "dps", "value": 5}],
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("name", resp.json()["roles"]["1"])

    def test_new_entry_long_role_name(self):
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id,
            roles=[{"name": "x" * 65, "value": 10}],
            shares=[
                {
                    "character_id": self.owner_char.character_id,
                    "helped_setup": False,
                    "site_count": 1,
                    "role_name": "x" * 65,
                }
            ],
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("name", resp.json()["roles"]["0"])

    def test_new_entry_negative_role_value(self):
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id, roles=[{"name": "dps", "value": -1}]
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("value", resp.json()["roles"]["0"])

    def test_new_entry_no_shares(self):
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(self.owner_char.character_id, shares=[])
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(resp.json()["shares_root"])

    def test_new_entry_nonexistent_character(self):
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id,
            shares=[
                {
                    "character_id": 88888888,
                    "helped_setup": False,
                    "site_count": 1,
                    "role_name": "dps",
                }
            ],
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("character_id", resp.json()["shares"]["0"])

    def test_new_entry_unowned_character(self):
        unowned = EveCharacter.objects.create(
            character_id=88888889, character_name="Unowned", corporation_id=1
        )
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id,
            shares=[
                {
                    "character_id": unowned.character_id,
                    "helped_setup": False,
                    "site_count": 1,
                    "role_name": "dps",
                }
            ],
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("character_id", resp.json()["shares"]["0"])

    def test_new_entry_duplicate_character(self):
        self.client.force_login(self.owner)
        share = {
            "character_id": self.owner_char.character_id,
            "helped_setup": False,
            "site_count": 1,
            "role_name": "dps",
        }
        payload = self.valid_entry_payload(
            self.owner_char.character_id, shares=[share, dict(share)]
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("character_id", resp.json()["shares"]["1"])

    def test_new_entry_bad_role_name(self):
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id,
            shares=[
                {
                    "character_id": self.owner_char.character_id,
                    "helped_setup": False,
                    "site_count": 1,
                    "role_name": "nope",
                }
            ],
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("role_name", resp.json()["shares"]["0"])

    def test_new_entry_zero_total_share_value(self):
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id, roles=[{"name": "dps", "value": 0}]
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(resp.json()["shares_root"])

    def test_new_entry_ignored_item(self):
        ignored = self.make_item(99500080, "Ignored", group_id=880)
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id, items=[{"id": ignored.id, "quantity": 1}]
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("item", resp.json()["items"]["0"])

    def test_new_entry_unpublished_item(self):
        unpub = self.make_item(99500081, "Unpub", published=False)
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id, items=[{"id": unpub.id, "quantity": 1}]
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("item", resp.json()["items"]["0"])

    def test_new_entry_bad_quantity(self):
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id, items=[{"id": self.item.id, "quantity": 0}]
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("quantity", resp.json()["items"]["0"])

    def test_new_entry_negative_estimated_total(self):
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id, estimated_total=-1
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(resp.json()["estimated_total"])

    def test_new_entry_zero_total_no_items(self):
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id, estimated_total=0, items=[]
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(resp.json()["estimated_total"])

    def test_new_entry_inactive_funding_project(self):
        project = FundingProject.objects.create(
            name="inactive", goal=1, is_active=False
        )
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id,
            funding_project_id=project.pk,
            funding_percentage=50,
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(resp.json()["funding_project_id"])

    def test_new_entry_funding_percentage_required(self):
        project = FundingProject.objects.create(name="active1", goal=1)
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id,
            funding_project_id=project.pk,
            funding_percentage=None,
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(resp.json()["funding_percentage"])

    def test_new_entry_funding_percentage_out_of_range(self):
        project = FundingProject.objects.create(name="active2", goal=1)
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id,
            funding_project_id=project.pk,
            funding_percentage=150,
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(resp.json()["funding_percentage"])

    # ---- PVE_ONLY_MAINS rule ----

    def test_new_entry_two_chars_same_user_allowed_by_default(self):
        alt = self.add_alt(self.owner, 90500050, "OwnerAlt")
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id,
            shares=[
                {
                    "character_id": self.owner_char.character_id,
                    "helped_setup": False,
                    "site_count": 1,
                    "role_name": "dps",
                },
                {
                    "character_id": alt.character_id,
                    "helped_setup": False,
                    "site_count": 1,
                    "role_name": "dps",
                },
            ],
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 200, resp.content)

    @patch("allianceauth_pve.api.schema.PVE_ONLY_MAINS", new=True)
    def test_new_entry_two_chars_same_user_blocked_when_only_mains(self):
        alt = self.add_alt(self.owner, 90500051, "OwnerAlt2")
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id,
            shares=[
                {
                    "character_id": self.owner_char.character_id,
                    "helped_setup": False,
                    "site_count": 1,
                    "role_name": "dps",
                },
                {
                    "character_id": alt.character_id,
                    "helped_setup": False,
                    "site_count": 1,
                    "role_name": "dps",
                },
            ],
        )
        resp = self.api_request(
            "POST", "new_entry", payload, rotation_id=self.rotation.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn(
            "A user can only have one share in the entry.",
            resp.json()["shares"]["1"]["character_id"],
        )

    # ---- get_entry_for_edit ----

    def test_get_entry_for_edit_success(self):
        self.client.force_login(self.owner)
        resp = self.client.get(
            url(
                "get_entry_for_edit",
                rotation_id=self.rotation.pk,
                entry_id=self.entry.pk,
            )
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["roles"]), 1)
        self.assertEqual(len(data["shares"]), 1)

    def test_get_entry_for_edit_not_owner(self):
        self.client.force_login(self.other)
        resp = self.client.get(
            url(
                "get_entry_for_edit",
                rotation_id=self.rotation.pk,
                entry_id=self.entry.pk,
            )
        )
        self.assertEqual(resp.status_code, 403)

    def test_get_entry_for_edit_closed_rotation(self):
        rotation = self.make_rotation(name="editclosed")
        entry, _, _ = self.make_entry(rotation, self.owner, self.owner_char)
        rotation.is_closed = True
        rotation.save()
        self.client.force_login(self.owner)
        resp = self.client.get(
            url("get_entry_for_edit", rotation_id=rotation.pk, entry_id=entry.pk)
        )
        self.assertEqual(resp.status_code, 403)

    def test_get_entry_for_edit_share_without_main(self):
        nomain = AuthUtils.create_user("ent_nomain")
        nomain_char = EveCharacter.objects.create(
            character_id=90500060, character_name="NoMainChar", corporation_id=1
        )
        self.make_ownership(nomain, nomain_char)
        rotation = self.make_rotation(name="nomainrot")
        entry, role, _ = self.make_entry(rotation, self.owner, self.owner_char)
        EntryCharacter.objects.create(
            entry=entry,
            user=nomain,
            user_character=nomain_char,
            role=role,
            site_count=1,
        )
        self.client.force_login(self.owner)
        resp = self.client.get(
            url("get_entry_for_edit", rotation_id=rotation.pk, entry_id=entry.pk)
        )
        self.assertEqual(resp.status_code, 403)

    def test_get_entry_for_edit_404(self):
        self.client.force_login(self.owner)
        resp = self.client.get(
            url("get_entry_for_edit", rotation_id=self.rotation.pk, entry_id=999999)
        )
        self.assertEqual(resp.status_code, 404)

    # ---- edit_entry ----

    def test_edit_entry_success(self):
        rotation = self.make_rotation(name="editrot")
        entry, _, _ = self.make_entry(rotation, self.owner, self.owner_char)
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(
            self.owner_char.character_id,
            roles=[{"name": "newrole", "value": 7}],
            shares=[
                {
                    "character_id": self.owner_char.character_id,
                    "helped_setup": False,
                    "site_count": 3,
                    "role_name": "newrole",
                }
            ],
        )
        resp = self.api_request(
            "POST", "edit_entry", payload, rotation_id=rotation.pk, entry_id=entry.pk
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        entry.refresh_from_db()
        self.assertEqual(entry.roles.get().name, "newrole")
        self.assertEqual(entry.ratting_shares.get().site_count, 3)

    def test_edit_entry_not_owner(self):
        self.client.force_login(self.other)
        resp = self.api_request(
            "POST",
            "edit_entry",
            self.valid_entry_payload(self.owner_char.character_id),
            rotation_id=self.rotation.pk,
            entry_id=self.entry.pk,
        )
        self.assertEqual(resp.status_code, 403)

    def test_edit_entry_closed_rotation(self):
        rotation = self.make_rotation(name="editclosed2")
        entry, _, _ = self.make_entry(rotation, self.owner, self.owner_char)
        rotation.is_closed = True
        rotation.save()
        self.client.force_login(self.owner)
        resp = self.api_request(
            "POST",
            "edit_entry",
            self.valid_entry_payload(self.owner_char.character_id),
            rotation_id=rotation.pk,
            entry_id=entry.pk,
        )
        self.assertEqual(resp.status_code, 403)

    def test_edit_entry_404(self):
        self.client.force_login(self.owner)
        resp = self.api_request(
            "POST",
            "edit_entry",
            self.valid_entry_payload(self.owner_char.character_id),
            rotation_id=self.rotation.pk,
            entry_id=999999,
        )
        self.assertEqual(resp.status_code, 404)

    def test_edit_entry_validation_error(self):
        rotation = self.make_rotation(name="editbad")
        entry, _, _ = self.make_entry(rotation, self.owner, self.owner_char)
        self.client.force_login(self.owner)
        payload = self.valid_entry_payload(self.owner_char.character_id, roles=[])
        resp = self.api_request(
            "POST", "edit_entry", payload, rotation_id=rotation.pk, entry_id=entry.pk
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(resp.json()["roles_root"])

    # ---- delete_rotation_entry ----

    def test_delete_entry_owner(self):
        rotation = self.make_rotation(name="delrot")
        entry, _, _ = self.make_entry(rotation, self.owner, self.owner_char)
        self.client.force_login(self.owner)
        resp = self.client.delete(
            url("delete_rotation_entry", rotation_id=rotation.pk, entry_id=entry.pk)
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Entry.objects.filter(pk=entry.pk).exists())

    def test_delete_entry_non_owner_forbidden(self):
        rotation = self.make_rotation(name="delrot2")
        entry, _, _ = self.make_entry(rotation, self.owner, self.owner_char)
        self.client.force_login(self.other)
        resp = self.client.delete(
            url("delete_rotation_entry", rotation_id=rotation.pk, entry_id=entry.pk)
        )
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(Entry.objects.filter(pk=entry.pk).exists())

    def test_delete_entry_closed_rotation(self):
        rotation = self.make_rotation(name="delclosed")
        entry, _, _ = self.make_entry(rotation, self.owner, self.owner_char)
        rotation.is_closed = True
        rotation.save()
        self.client.force_login(self.owner)
        resp = self.client.delete(
            url("delete_rotation_entry", rotation_id=rotation.pk, entry_id=entry.pk)
        )
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(Entry.objects.filter(pk=entry.pk).exists())

    def test_delete_entry_superuser_non_owner(self):
        rotation = self.make_rotation(name="delsuper")
        entry, _, _ = self.make_entry(rotation, self.owner, self.owner_char)
        self.client.force_login(self.superuser)
        resp = self.client.delete(
            url("delete_rotation_entry", rotation_id=rotation.pk, entry_id=entry.pk)
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Entry.objects.filter(pk=entry.pk).exists())

    def test_delete_entry_404(self):
        self.client.force_login(self.owner)
        resp = self.client.delete(
            url("delete_rotation_entry", rotation_id=self.rotation.pk, entry_id=999999)
        )
        self.assertEqual(resp.status_code, 404)
