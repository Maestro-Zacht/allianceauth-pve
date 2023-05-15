import datetime

from django.test import TestCase
from django.utils import timezone

from allianceauth.tests.auth_utils import AuthUtils
from allianceauth.authentication.models import CharacterOwnership

from ..models import Rotation, Entry, EntryCharacter, EntryRole
from ..actions import running_averages, check_forms_valid
from ..forms import NewRoleFormSet, NewEntryForm, NewShareFormSet


class TestRunningAverages(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        rotation: Rotation = Rotation.objects.create(
            name='test1rot'
        )

        entry: Entry = Entry.objects.create(
            rotation=rotation,
            created_by=cls.testuser,
            estimated_total=1_000_000_000
        )

        role = EntryRole.objects.create(
            entry=entry,
            name='testrole1',
            value=1
        )

        share = EntryCharacter.objects.create(
            entry=entry,
            user=cls.testuser,
            user_character=cls.testcharacter,
            role=role,
            site_count=1,
            helped_setup=False
        )

        rotation.actual_total = 900_000_000
        rotation.is_closed = True
        rotation.closed_at = timezone.now()
        rotation.save()

    def test_valid_interval(self):
        res = running_averages(self.testuser, timezone.now() - datetime.timedelta(days=1), timezone.now() + datetime.timedelta(days=1))

        self.assertEqual(res['estimated_total'], 1_000_000_000)
        self.assertEqual(res['actual_total'], 900_000_000)
        self.assertEqual(res['helped_setups'], 0)

    def test_empty_interval(self):
        res = running_averages(self.testuser, timezone.now() - datetime.timedelta(days=2), timezone.now() - datetime.timedelta(days=1))

        self.assertDictEqual(res, {})


class TestCheckFormsValid(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)
        CharacterOwnership.objects.create(character=cls.testcharacter, user=cls.testuser, owner_hash='aa1')

        cls.testuser2 = AuthUtils.create_user('aauth_testuser2')
        cls.testcharacter2 = AuthUtils.add_main_character_2(cls.testuser2, 'aauth_testchar2random', 795853496)
        CharacterOwnership.objects.create(character=cls.testcharacter2, user=cls.testuser2, owner_hash='aa2')

        cls.form_data = {
            'roles-TOTAL_FORMS': '1',
            'roles-INITIAL_FORMS': '1',
            'roles-MIN_NUM_FORMS': '1',
            'roles-MAX_NUM_FORMS': '1000',
            'roles-0-name': 'Krab',
            'roles-0-value': '1',
            'estimated_total': '553400000',
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-user': cls.testuser.pk,
            'form-0-character': cls.testcharacter.pk,
            'form-0-role': 'Krab',
            'form-0-site_count': '1'
        }

    def get_forms(self):
        return (
            NewRoleFormSet(self.form_data, prefix='roles'),
            NewEntryForm(self.form_data),
            NewShareFormSet(self.form_data),
        )

    def test_invalid_role_form(self):
        self.form_data['roles-0-value'] = '-1'

        errors = check_forms_valid(*self.get_forms())

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], 'Error in roles')

    def test_invalid_entry_form(self):
        self.form_data['estimated_total'] = '0'

        errors = check_forms_valid(*self.get_forms())

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], 'Entry form or shares are not correct')

    def test_invalid_share_form(self):
        self.form_data['form-0-site_count'] = '-1'

        errors = check_forms_valid(*self.get_forms())

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], 'Entry form or shares are not correct')

    def test_no_shares(self):
        self.form_data.pop('form-0-user')
        self.form_data.pop('form-0-character')
        self.form_data.pop('form-0-role')
        self.form_data.pop('form-0-site_count')
        self.form_data['form-TOTAL_FORMS'] = '0'

        errors = check_forms_valid(*self.get_forms())

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], 'Not enough shares or roles')

    def test_no_loot_given(self):
        self.form_data.update({
            'roles-TOTAL_FORMS': '2',
            'roles-0-value': '0',
            'roles-1-value': '1',
            'roles-1-name': 'Krab2',
            'form-TOTAL_FORMS': '2',
            'form-1-user': self.testuser2.pk,
            'form-1-character': self.testcharacter2.pk,
            'form-1-role': 'Krab',
            'form-1-site_count': '0',
        })

        errors = check_forms_valid(*self.get_forms())

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], 'Form not valid, you need at least 1 person to receive loot')

    def test_valid(self):
        errors = check_forms_valid(*self.get_forms())
        self.assertEqual(len(errors), 0)
