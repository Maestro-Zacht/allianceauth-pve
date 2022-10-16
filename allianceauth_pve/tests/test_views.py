from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.messages import get_messages
from django.db.models import Sum

from allianceauth.tests.auth_utils import AuthUtils
from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter

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
            estimated_total=1_000_000_000
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
            'sales_value': '900,000,000',
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
            'sales_value': '900,000,000',
        }

        response = self.client.post(reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]), form_data)

        self.assertEqual(response.status_code, 200)

        self.rotation.refresh_from_db()
        self.assertFalse(self.rotation.is_closed)
        self.assertEqual(self.rotation.actual_total, 0)

        self.assertTemplateUsed(response, 'allianceauth_pve/rotation.html')


class TestGetAvaiableRatters(TestCase):
    maxDiff = None

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
                        'char_status': 'Main',
                        'char_tooltip': '',
                    },
                    {
                        'character_id': self.testcharacter2.pk,
                        'character_name': self.testcharacter2.character_name,
                        'profile_pic': self.testcharacter2.portrait_url_32,
                        'user_id': self.testuser2.pk,
                        'user_main_character_name': self.testcharacter2.character_name,
                        'user_pic': self.testcharacter2.portrait_url_32,
                        'char_status': 'Main',
                        'char_tooltip': '',
                    }
                ]
            }
        )

    def test_no_name_exclude(self):
        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:all_ratters'), {'excludeIds': self.testcharacter.pk})

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                'result': [
                    {
                        'character_id': self.testcharacter2.pk,
                        'character_name': self.testcharacter2.character_name,
                        'profile_pic': self.testcharacter2.portrait_url_32,
                        'user_id': self.testuser2.pk,
                        'user_main_character_name': self.testcharacter2.character_name,
                        'user_pic': self.testcharacter2.portrait_url_32,
                        'char_status': 'Main',
                        'char_tooltip': '',
                    }
                ]
            }
        )

    def test_name_no_exclude(self):
        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:search_ratters', args=['random']))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                'result': [
                    {
                        'character_id': self.testcharacter2.pk,
                        'character_name': self.testcharacter2.character_name,
                        'profile_pic': self.testcharacter2.portrait_url_32,
                        'user_id': self.testuser2.pk,
                        'user_main_character_name': self.testcharacter2.character_name,
                        'user_pic': self.testcharacter2.portrait_url_32,
                        'char_status': 'Main',
                        'char_tooltip': '',
                    }
                ]
            }
        )

    def test_name_exclude(self):
        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:search_ratters', args=['random']), {'excludeIds': self.testcharacter2.pk})

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'result': []})

    @override_settings(PVE_ONLY_MAINS=True)
    def test_alt_name_only_main(self):
        self.client.force_login(self.testuser)

        testcharacter2bis = EveCharacter.objects.create(
            character_id=1510588747,
            character_name='aauth_testchar3bis',
            corporation_id=int(2345),
            corporation_name='',
            corporation_ticker='',
            alliance_id=None,
            alliance_name='',
            faction_id=None,
            faction_name=''
        )
        CharacterOwnership.objects.create(character=testcharacter2bis, user=self.testuser2, owner_hash='aa2bis')

        response = self.client.get(reverse('allianceauth_pve:search_ratters', args=['bis']))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                'result': [
                    {
                        'character_id': self.testcharacter2.pk,
                        'character_name': self.testcharacter2.character_name,
                        'profile_pic': self.testcharacter2.portrait_url_32,
                        'user_id': self.testuser2.pk,
                        'user_main_character_name': self.testcharacter2.character_name,
                        'user_pic': self.testcharacter2.portrait_url_32,
                        'char_status': 'Main',
                        'char_tooltip': testcharacter2bis.character_name,
                    }
                ]
            }
        )

    def test_alt_name(self):
        self.client.force_login(self.testuser)

        testcharacter2bis = EveCharacter.objects.create(
            character_id=1510588747,
            character_name='aauth_testchar3bis',
            corporation_id=int(2345),
            corporation_name='',
            corporation_ticker='',
            alliance_id=None,
            alliance_name='',
            faction_id=None,
            faction_name=''
        )
        CharacterOwnership.objects.create(character=testcharacter2bis, user=self.testuser2, owner_hash='aa2bis')

        testcharacter2tris = EveCharacter.objects.create(
            character_id=391334192,
            character_name='aauth_testchar3tris',
            corporation_id=int(2345),
            corporation_name='',
            corporation_ticker='',
            alliance_id=None,
            alliance_name='',
            faction_id=None,
            faction_name=''
        )
        CharacterOwnership.objects.create(character=testcharacter2tris, user=self.testuser2, owner_hash='aa2tris')

        response = self.client.get(reverse('allianceauth_pve:search_ratters', args=['bis']))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                'result': [
                    {
                        'character_id': self.testcharacter2.pk,
                        'character_name': self.testcharacter2.character_name,
                        'profile_pic': self.testcharacter2.portrait_url_32,
                        'user_id': self.testuser2.pk,
                        'user_main_character_name': self.testcharacter2.character_name,
                        'user_pic': self.testcharacter2.portrait_url_32,
                        'char_status': 'Main',
                        'char_tooltip': f'{testcharacter2bis.character_name}, {testcharacter2tris.character_name}',
                    },
                    {
                        'character_id': testcharacter2bis.pk,
                        'character_name': testcharacter2bis.character_name,
                        'profile_pic': testcharacter2bis.portrait_url_32,
                        'user_id': self.testuser2.pk,
                        'user_main_character_name': self.testcharacter2.character_name,
                        'user_pic': self.testcharacter2.portrait_url_32,
                        'char_status': 'Alt',
                        'char_tooltip': self.testcharacter2.character_name,
                    }
                ]
            }
        )


class TestAddEntryView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)
        CharacterOwnership.objects.create(character=cls.testcharacter, user=cls.testuser, owner_hash='aa1')

        cls.testuser2 = AuthUtils.create_user('aauth_testuser2')
        cls.testcharacter2 = AuthUtils.add_main_character_2(cls.testuser2, 'aauth_testchar2random', 795853496)
        CharacterOwnership.objects.create(character=cls.testcharacter2, user=cls.testuser2, owner_hash='aa2')

        cls.testuser = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.access_pve', 'allianceauth_pve.manage_entries'], cls.testuser)

        cls.testuser2 = AuthUtils.add_permissions_to_user_by_name(['allianceauth_pve.access_pve', 'allianceauth_pve.manage_entries'], cls.testuser2)

        cls.rotation: Rotation = Rotation.objects.create(
            name='test1rot'
        )

        cls.entry: Entry = Entry.objects.create(
            rotation=cls.rotation,
            created_by=cls.testuser,
            estimated_total=1_000_000_000
        )

        cls.role: EntryRole = EntryRole.objects.create(
            entry=cls.entry,
            name='Krab',
            value=1
        )

        EntryCharacter.objects.create(
            entry=cls.entry,
            user=cls.testuser,
            user_character=cls.testcharacter,
            role=cls.role,
            site_count=1,
            helped_setup=False
        )

    def test_rotation_closed(self):
        self.rotation.is_closed = True
        self.rotation.save()

        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:new_entry', args=[self.rotation.pk]))

        self.assertRedirects(response, reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]))

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, 'The rotation is closed, you cannot add an entry')

    def test_wrong_rotation(self):
        rot = Rotation.objects.create(name='otherrot')

        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:edit_entry', args=[rot.pk, self.entry.pk]))

        self.assertRedirects(response, reverse('allianceauth_pve:rotation_view', args=[rot.pk]))

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "The selected entry doesn't belong to the selected rotation")

    def test_user_not_allowed(self):
        self.client.force_login(self.testuser2)

        response = self.client.get(reverse('allianceauth_pve:edit_entry', args=[self.rotation.pk, self.entry.pk]))

        self.assertRedirects(response, reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]))

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "You cannot edit this entry")

    def test_valid_get_new_entry(self):
        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:new_entry', args=[self.rotation.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'allianceauth_pve/entry_form.html')

    def test_valid_get_edit_entry(self):
        self.client.force_login(self.testuser)

        response = self.client.get(reverse('allianceauth_pve:edit_entry', args=[self.rotation.pk, self.entry.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'allianceauth_pve/entry_form.html')

    def test_invalid_form(self):
        self.client.force_login(self.testuser)

        form_data = {
            'roles-TOTAL_FORMS': '2',
            'roles-INITIAL_FORMS': '1',
            'roles-MIN_NUM_FORMS': '1',
            'roles-MAX_NUM_FORMS': '1000',
            'roles-0-name': 'Krab',
            'roles-0-value': '1',
            'roles-1-name': 'Krab2',
            'roles-1-value': '0',
            'estimated_total': '1660200000',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-user': self.testuser.pk,
            'form-0-character': self.testcharacter.pk,
            'form-0-role': 'Krab2',
            'form-0-helped_setup': 'on',
            'form-0-site_count': '2',
            'form-1-user': self.testuser2.pk,
            'form-1-character': self.testcharacter2.pk,
            'form-1-role': 'Krab',
            'form-1-site_count': '0'
        }

        response = self.client.post(reverse('allianceauth_pve:new_entry', args=[self.rotation.pk]), form_data)

        self.assertEqual(response.status_code, 200)

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, 'Error: Form not valid, you need at least 1 person to receive loot')

    def test_post_valid_new_entry(self):
        self.client.force_login(self.testuser)

        form_data = {
            'roles-TOTAL_FORMS': '1',
            'roles-INITIAL_FORMS': '1',
            'roles-MIN_NUM_FORMS': '1',
            'roles-MAX_NUM_FORMS': '1000',
            'roles-0-name': 'Krab',
            'roles-0-value': '1',
            'estimated_total': '1660200000',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-user': self.testuser.pk,
            'form-0-character': self.testcharacter.pk,
            'form-0-role': 'Krab',
            'form-0-helped_setup': 'on',
            'form-0-site_count': '2',
            'form-1-user': self.testuser2.pk,
            'form-1-character': self.testcharacter2.pk,
            'form-1-role': 'Krab',
            'form-1-site_count': '1'
        }

        response = self.client.post(reverse('allianceauth_pve:new_entry', args=[self.rotation.pk]), form_data)

        self.assertRedirects(response, reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]))

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Entry added successfully")

        self.assertEqual(self.rotation.entries.exclude(pk=self.entry.pk).count(), 1)

        entry: Entry = self.rotation.entries.exclude(pk=self.entry.pk).get()

        self.assertEqual(entry.roles.count(), 1)
        role: EntryRole = entry.roles.get()
        self.assertEqual(role.name, 'Krab')
        self.assertEqual(role.value, 1)

        self.assertEqual(entry.ratting_shares.count(), 2)

        estimated_total = entry.ratting_shares.with_totals().aggregate(val=Sum('estimated_share_total'))['val']
        self.assertAlmostEqual(estimated_total, 1660200000.0)
        self.assertAlmostEqual(estimated_total, entry.estimated_total)

    def test_post_valid_edit_entry(self):
        self.client.force_login(self.testuser)

        form_data = {
            'roles-TOTAL_FORMS': '1',
            'roles-INITIAL_FORMS': '1',
            'roles-MIN_NUM_FORMS': '1',
            'roles-MAX_NUM_FORMS': '1000',
            'roles-0-name': 'Krabs',
            'roles-0-value': '1',
            'estimated_total': '1660200000',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-user': self.testuser.pk,
            'form-0-character': self.testcharacter.pk,
            'form-0-role': 'Krabs',
            'form-0-helped_setup': 'on',
            'form-0-site_count': '2',
            'form-1-user': self.testuser2.pk,
            'form-1-character': self.testcharacter2.pk,
            'form-1-role': 'Krabs',
            'form-1-site_count': '1'
        }

        response = self.client.post(reverse('allianceauth_pve:edit_entry', args=[self.rotation.pk, self.entry.pk]), form_data)

        self.assertRedirects(response, reverse('allianceauth_pve:rotation_view', args=[self.rotation.pk]))

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Entry added successfully")

        self.assertEqual(self.rotation.entries.count(), 1)

        self.entry.refresh_from_db()

        self.assertEqual(self.entry.roles.count(), 1)
        role: EntryRole = self.entry.roles.get()
        self.assertEqual(role.name, 'Krabs')
        self.assertEqual(role.value, 1)

        self.assertEqual(self.entry.ratting_shares.count(), 2)

        estimated_total = self.entry.ratting_shares.with_totals().aggregate(val=Sum('estimated_share_total'))['val']
        self.assertAlmostEqual(estimated_total, 1660200000.0)
        self.assertAlmostEqual(estimated_total, self.entry.estimated_total)


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
            estimated_total=1_000_000_000
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
