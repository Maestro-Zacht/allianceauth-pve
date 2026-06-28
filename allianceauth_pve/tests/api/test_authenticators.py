from allianceauth_pve.tests.utils import ACCESS, PveApiTestBase, url


class TestApiAuthGating(PveApiTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.no_access, _ = cls.make_user("gate_noaccess", 90100001, "NoAccess")
        cls.access_only, char2 = cls.make_user(
            "gate_access", 90100002, "AccessOnly", perms=[ACCESS]
        )
        cls.rotation = cls.make_rotation(name="gaterot")
        cls.entry, _, _ = cls.make_entry(
            cls.rotation,
            cls.access_only,
            char2,
        )

    def test_unauthenticated_redirects(self):
        resp = self.client.get(url("list_rotations"))
        self.assertEqual(resp.status_code, 302)

    def test_logged_in_without_access_pve_401(self):
        self.client.force_login(self.no_access)
        resp = self.client.get(url("list_rotations"))
        self.assertEqual(resp.status_code, 401)

    def test_access_only_can_read(self):
        self.client.force_login(self.access_only)
        resp = self.client.get(url("list_rotations"))
        self.assertEqual(resp.status_code, 200)

    def test_access_only_blocked_on_mutating_endpoints(self):
        self.client.force_login(self.access_only)
        rid = self.rotation.pk
        eid = self.entry.pk

        cases = [
            ("POST", "create_rotation", {}),
            ("PATCH", "close_rotation", {"rotation_id": rid}),
            ("POST", "new_entry", {"rotation_id": rid}),
            ("POST", "edit_entry", {"rotation_id": rid, "entry_id": eid}),
            ("DELETE", "delete_rotation_entry", {"rotation_id": rid, "entry_id": eid}),
            ("GET", "get_entry_for_edit", {"rotation_id": rid, "entry_id": eid}),
            ("POST", "create_project", {}),
            ("POST", "toggle_complete_project", {"project_id": 1}),
            ("POST", "search_ratters", {}),
            ("POST", "search_items", {}),
        ]

        for method, name, kwargs in cases:
            with self.subTest(method=method, target=name):
                resp = self.api_request(method, name, **kwargs)
                self.assertEqual(resp.status_code, 401)
