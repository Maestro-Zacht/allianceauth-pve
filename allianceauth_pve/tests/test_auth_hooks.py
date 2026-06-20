from allianceauth.tests.auth_utils import AuthUtils
from django.test import TestCase
from django.urls import reverse


class TestHooks(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.html_menu = "PvE Tool"

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user("aauth_testuser")
        cls.testcharacter = AuthUtils.add_main_character_2(
            cls.testuser, "aauth_testchar", 2116790529
        )

    def test_render_hook_success(self):
        user = AuthUtils.add_permission_to_user_by_name(
            "allianceauth_pve.access_pve", self.testuser
        )

        self.client.force_login(user)

        response = self.client.get(reverse("allianceauth_pve:react_view"))
        self.assertContains(response, self.html_menu, html=True)

    def test_render_hook_fail(self):
        self.client.force_login(self.testuser)

        response = self.client.get(reverse("authentication:dashboard"))
        self.assertNotContains(response, self.html_menu, html=True)
