from django.test import TestCase
from django.urls import reverse

from allianceauth.tests.auth_utils import AuthUtils

from ..models import Rotation, Entry


class TestIndexView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.testuser = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.access_pve'], cls.testuser)

    def test_index(self):
        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:index'))
        self.assertRedirects(response, reverse('allianceauth_pve:dashboard'))


class TestDashboardView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.testuser = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.access_pve'], cls.testuser)

    def test_dashboard(self):
        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:dashboard'))

        self.assertTemplateUsed(response, 'allianceauth_pve/ratting-dashboard.html')


class TestDeleteEntryView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.testuser2 = AuthUtils.create_user('aauth_testuser2')
        cls.testcharacter2 = AuthUtils.add_main_character_2(cls.testuser2, 'aauth_testchar2', 795853496)

        cls.testuser = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.access_pve', 'allianceauth_pve.manage_entries'], cls.testuser)

        cls.testuser2 = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.access_pve', 'allianceauth_pve.manage_entries'], cls.testuser2)

        cls.rotation: Rotation = Rotation.objects.create(
            name='test1rot'
        )

        cls.entry: Entry = Entry.objects.create(
            rotation=cls.rotation,
            created_by=cls.testuser,
            estimated_total=1_000_000_000.0
        )

    def test_delete_success(self):
        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:delete_entry', args=[self.entry.pk]))

        self.assertRedirects(response, reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]))
        self.assertEqual(self.rotation.entries.count(), 0)

    def test_delete_fail_rotation_closed(self):
        self.client.force_login(self.testuser)

        self.rotation.is_closed = True
        self.rotation.save()

        response = self.client.get(reverse('allianceauth_pve:delete_entry', args=[self.entry.pk]))

        self.assertRedirects(response, reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]))
        self.assertEqual(self.rotation.entries.count(), 1)

    def test_delete_fail_different_user(self):
        self.client.force_login(self.testuser2)

        response = self.client.get(reverse('allianceauth_pve:delete_entry', args=[self.entry.pk]))

        self.assertRedirects(response, reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]))
        self.assertEqual(self.rotation.entries.count(), 1)


class TestCreateRotationView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.testuser = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.access_pve', 'allianceauth_pve.manage_rotations'], cls.testuser)

    def test_get(self):
        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:new_rotation'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'allianceauth_pve/rotation_create.html')

    def test_post_success(self):
        self.client.force_login(self.testuser)

        form_data = {
            'name': 'testrot1',
            'priority': '1',
            'tax_rate': '1.0',
        }

        response = self.client.post(reverse('allianceauth_pve:new_rotation'), form_data)

        self.assertEqual(Rotation.objects.count(), 1)

        rotation = Rotation.objects.get(name='testrot1')

        self.assertRedirects(response, reverse('allianceauth_pve:rotation_view', args=[rotation.pk]))

    def test_post_invalid(self):
        self.client.force_login(self.testuser)

        form_data = {
            'name': 'testrot1',
            'priority': '1',
            'tax_rate': '1.0',
            'min_people_share_setup': '-5'
        }

        response = self.client.post(reverse('allianceauth_pve:new_rotation'), form_data)

        self.assertTemplateUsed(response, 'allianceauth_pve/rotation_create.html')
