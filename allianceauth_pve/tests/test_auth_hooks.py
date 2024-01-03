from django.test import TestCase
from django.urls import reverse

from allianceauth.tests.auth_utils import AuthUtils


class TestHooks(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.html_menu = f"""
            <a class="nav-link flex-fill align-self-center" href="/pve/">
                PvE Tool
            </a>
        """

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

    def test_render_hook_success(self):
        user = AuthUtils.add_permission_to_user_by_name('allianceauth_pve.access_pve', self.testuser)

        self.client.force_login(user)

        response = self.client.get(reverse('allianceauth_pve:dashboard'))
        self.assertContains(response, self.html_menu, html=True)

    def test_render_hook_fail(self):
        self.testuser = AuthUtils.add_permission_to_user_by_name('allianceauth_pve.manage_rotations', self.testuser)

        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:new_rotation'))
        self.assertNotContains(response, self.html_menu, html=True)
