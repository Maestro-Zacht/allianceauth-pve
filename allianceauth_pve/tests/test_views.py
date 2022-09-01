from django.test import TestCase
from django.urls import reverse

from allianceauth.tests.auth_utils import AuthUtils
from allianceauth.authentication.models import CharacterOwnership

from ..models import Rotation, Entry, EntryCharacter, EntryRole


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


class TestRotationView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.testuser = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.access_pve'], cls.testuser)

        cls.rotation: Rotation = Rotation.objects.create(
            name='test1rot'
        )

        entry = Entry.objects.create(
            rotation=cls.rotation,
            created_by=cls.testuser,
            estimated_total=1_000_000_000.0
        )

        role = EntryRole.objects.create(
            entry=entry,
            name='testrole1',
            value=1
        )

        EntryCharacter.objects.create(
            entry=entry,
            user=cls.testuser,
            user_character=cls.testcharacter,
            role=role,
            site_count=1,
            helped_setup=False
        )

    def test_rotation_open(self):
        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]))

        self.assertTemplateUsed(response, 'allianceauth_pve/rotation.html')

    def test_rotation_closed(self):
        self.rotation.is_closed = True
        self.rotation.save()

        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]))

        self.assertTemplateUsed(response, 'allianceauth_pve/rotation.html')

    def test_close_rotation_valid(self):
        self.testuser = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.manage_rotations'], self.testuser)

        self.client.force_login(self.testuser)

        form_data = {
            'sales_value': '900000000',
        }

        response = self.client.post(reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]), form_data)

        self.assertEqual(response.status_code, 200)

        self.rotation.refresh_from_db()
        self.assertTrue(self.rotation.is_closed)
        self.assertEqual(self.rotation.actual_total, 900000000)

        self.assertTemplateUsed(response, 'allianceauth_pve/rotation.html')

    def test_close_rotation_invalid(self):
        self.testuser = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.manage_rotations'], self.testuser)

        self.client.force_login(self.testuser)

        form_data = {
            'sales_value': '0',
        }

        response = self.client.post(reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]), form_data)

        self.assertEqual(response.status_code, 200)

        self.rotation.refresh_from_db()
        self.assertFalse(self.rotation.is_closed)
        self.assertEqual(self.rotation.actual_total, 0)

        self.assertTemplateUsed(response, 'allianceauth_pve/rotation.html')

    def test_close_rotation_invalid_perms(self):
        self.client.force_login(self.testuser)

        form_data = {
            'sales_value': '900000000',
        }

        response = self.client.post(reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]), form_data)

        self.assertEqual(response.status_code, 200)

        self.rotation.refresh_from_db()
        self.assertFalse(self.rotation.is_closed)
        self.assertEqual(self.rotation.actual_total, 0)

        self.assertTemplateUsed(response, 'allianceauth_pve/rotation.html')


class TestGetAvaiableRatters(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)
        CharacterOwnership.objects.create(character=cls.testcharacter, user=cls.testuser, owner_hash='aa1')

        cls.testuser2 = AuthUtils.create_user('aauth_testuser2')
        cls.testcharacter2 = AuthUtils.add_main_character_2(cls.testuser2, 'aauth_testchar2random', 795853496)
        CharacterOwnership.objects.create(character=cls.testcharacter2, user=cls.testuser2, owner_hash='aa2')

        cls.testuser3 = AuthUtils.create_user('aauth_testuser3')
        cls.testcharacter3 = AuthUtils.add_main_character_2(cls.testuser3, 'aauth_testchar3', 781335233)
        CharacterOwnership.objects.create(character=cls.testcharacter3, user=cls.testuser3, owner_hash='aa3')

        cls.testuser = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.access_pve', 'allianceauth_pve.manage_entries'], cls.testuser)

        cls.testuser2 = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.access_pve'], cls.testuser2)

    def test_no_name_no_exclude(self):
        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:all_ratters'))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                'result': [
                    {
                        'character_id': self.testcharacter.pk,
                        'character_name': self.testcharacter.character_name,
                        'profile_pic': self.testcharacter.portrait_url_32,
                        'user_id': self.testuser.pk,
                        'user_main_character_name': self.testcharacter.character_name,
                        'user_pic': self.testcharacter.portrait_url_32,
                    },
                    {
                        'character_id': self.testcharacter2.character_id,
                        'character_name': self.testcharacter2.character_name,
                        'profile_pic': self.testcharacter2.portrait_url_32,
                        'user_id': self.testuser2.pk,
                        'user_main_character_name': self.testcharacter2.character_name,
                        'user_pic': self.testcharacter2.portrait_url_32,
                    }
                ]
            }
        )


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
            'max_daily_setups': '1',
            'min_people_share_setup': '3',
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
            'max_daily_setups': '1',
            'min_people_share_setup': '-5'
        }

        response = self.client.post(reverse('allianceauth_pve:new_rotation'), form_data)

        self.assertTemplateUsed(response, 'allianceauth_pve/rotation_create.html')
