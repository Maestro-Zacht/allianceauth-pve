from django.test import TestCase
from django.urls import reverse

from allianceauth.tests.auth_utils import AuthUtils


class TestIndex(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.testuser = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.access_pve'], cls.testuser)

        cls.client.force_login(cls.testuser)

    def test_index(self):
        response = self.client.get(reverse('allianceauth_pve:index'))
        self.assertRedirects(response, reverse('allianceauth_pve:dashboard'))
