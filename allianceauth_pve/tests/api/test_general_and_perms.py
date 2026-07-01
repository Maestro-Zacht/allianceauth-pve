from allianceauth_pve.models import GeneralRole, PveButton, RoleSetup
from allianceauth_pve.tests.utils import ACCESS, MANAGE_ENTRIES, PveApiTestBase, url


class TestTopLevelAndPermissions(PveApiTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.user, _ = cls.make_user(
            "top_user", 90200001, "TopUser", perms=[ACCESS, MANAGE_ENTRIES]
        )

        cls.button1 = PveButton.objects.create(text="btn1", amount=10)
        cls.button2 = PveButton.objects.create(text="btn2", amount=20)

        cls.setup = RoleSetup.objects.create(name="setup1")
        cls.role1 = GeneralRole.objects.create(setup=cls.setup, name="dps", value=10)
        cls.role2 = GeneralRole.objects.create(setup=cls.setup, name="logi", value=5)

    def test_list_buttons(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("list_buttons"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), PveButton.objects.count())
        self.assertLessEqual({"btn1", "btn2"}, {b["text"] for b in data})

    def test_list_role_setups(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("list_role_setups"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertDictEqual(
            data[0],
            {
                "id": self.setup.pk,
                "name": self.setup.name,
            },
        )

    def test_list_permissions(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("list_permissions"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["main_character_id"], 90200001)
        self.assertTrue(data["access_pve"])
        self.assertTrue(data["manage_entries"])
        self.assertFalse(data["manage_rotations"])
        self.assertFalse(data["manage_funding_projects"])
        self.assertFalse(data["is_superuser"])

    def test_list_permissions_superuser(self):
        superuser, _ = self.make_superuser("top_super", 90200002, "TopSuper")
        self.client.force_login(superuser)
        resp = self.client.get(url("list_permissions"))
        data = resp.json()
        self.assertTrue(data["is_superuser"])
        # superuser implicitly has all perms
        self.assertTrue(data["access_pve"])
        self.assertTrue(data["manage_entries"])
        self.assertTrue(data["manage_rotations"])
        self.assertTrue(data["manage_funding_projects"])
        self.assertTrue(data["is_superuser"])
