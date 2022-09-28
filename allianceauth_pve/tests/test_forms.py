from django.test import SimpleTestCase, TestCase

from allianceauth.tests.auth_utils import AuthUtils
from allianceauth.authentication.models import CharacterOwnership

from ..forms import NewRoleFormSet, NewShareFormSet


class TestNewRoleFormSet(SimpleTestCase):

    def test_valid(self):
        valid_data = {
            'roles-TOTAL_FORMS': '5',
            'roles-INITIAL_FORMS': '0',
            'roles-MIN_NUM_FORMS': '1',
            'roles-MAX_NUM_FORMS': '1000',
            'roles-0-name': 'roleS0R0',
            'roles-0-value': '1',
            'roles-1-name': 'roleS0R1',
            'roles-1-value': '1',
            'roles-2-name': 'roleS0R2',
            'roles-2-value': '2',
            'roles-3-name': 'roleS0R3',
            'roles-3-value': '3',
            'roles-4-name': 'roleS0R4',
            'roles-4-value': '4'
        }

        role_form = NewRoleFormSet(valid_data, prefix='roles')

        self.assertTrue(role_form.is_valid())

    def test_duplicated_invalid(self):
        invalid_data = {
            'roles-TOTAL_FORMS': '5',
            'roles-INITIAL_FORMS': '0',
            'roles-MIN_NUM_FORMS': '1',
            'roles-MAX_NUM_FORMS': '1000',
            'roles-0-name': 'roleS0R1',
            'roles-0-value': '1',
            'roles-1-name': 'roleS0R1',
            'roles-1-value': '1',
            'roles-2-name': 'roleS0R2',
            'roles-2-value': '2',
            'roles-3-name': 'roleS0R3',
            'roles-3-value': '3',
            'roles-4-name': 'roleS0R4',
            'roles-4-value': '4'
        }

        role_form = NewRoleFormSet(invalid_data, prefix='roles')

        self.assertFalse(role_form.is_valid())

    def test_error_invalid(self):
        invalid_data = {
            'roles-TOTAL_FORMS': '5',
            'roles-INITIAL_FORMS': '0',
            'roles-MIN_NUM_FORMS': '1',
            'roles-MAX_NUM_FORMS': '1000',
            'roles-0-name': 'roleS0R0',
            'roles-0-value': '0',
            'roles-1-name': 'roleS0R1',
            'roles-1-value': '-1',
            'roles-2-name': 'roleS0R2',
            'roles-2-value': '2',
            'roles-3-name': 'roleS0R3',
            'roles-3-value': '3',
            'roles-4-name': 'roleS0R4',
            'roles-4-value': '4'
        }

        role_form = NewRoleFormSet(invalid_data, prefix='roles')

        self.assertFalse(role_form.is_valid())


class TestNewShareFormset(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)
        CharacterOwnership.objects.create(character=cls.testcharacter, user=cls.testuser, owner_hash='aa1')

        cls.testuser2 = AuthUtils.create_user('aauth_testuser2')
        cls.testcharacter2 = AuthUtils.add_main_character_2(cls.testuser2, 'aauth_testchar2', 795853496)
        CharacterOwnership.objects.create(character=cls.testcharacter2, user=cls.testuser2, owner_hash='aa2')

    def test_valid(self):
        valid_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-user': self.testuser.pk,
            'form-0-character': self.testcharacter.pk,
            'form-0-role': 'Krab',
            'form-0-site_count': '1',
            'form-1-user': self.testuser2.pk,
            'form-1-character': self.testcharacter2.pk,
            'form-1-role': 'Krab',
            'form-1-site_count': '1'
        }

        new_share_form = NewShareFormSet(valid_data)

        roles_choices = [('Krab', 'Krab')]
        for form in new_share_form:
            form.fields['role'].choices = roles_choices

        self.assertTrue(new_share_form.is_valid())

    def test_user_invalid(self):
        invalid_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-user': self.testuser.pk + 10**3,
            'form-0-character': self.testcharacter.pk,
            'form-0-role': 'Krab',
            'form-0-site_count': '1',
            'form-1-user': self.testuser2.pk,
            'form-1-character': self.testcharacter2.pk,
            'form-1-role': 'Krab',
            'form-1-site_count': '1'
        }

        new_share_form = NewShareFormSet(invalid_data)

        roles_choices = [('Krab', 'Krab')]
        for form in new_share_form:
            form.fields['role'].choices = roles_choices

        self.assertFalse(new_share_form.is_valid())

    def test_character_invalid(self):
        invalid_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-user': self.testuser.pk,
            'form-0-character': self.testcharacter.pk + 10**3,
            'form-0-role': 'Krab',
            'form-0-site_count': '1',
            'form-1-user': self.testuser2.pk,
            'form-1-character': self.testcharacter2.pk,
            'form-1-role': 'Krab',
            'form-1-site_count': '1'
        }

        new_share_form = NewShareFormSet(invalid_data)

        roles_choices = [('Krab', 'Krab')]
        for form in new_share_form:
            form.fields['role'].choices = roles_choices

        self.assertFalse(new_share_form.is_valid())

    def test_multishare_invalid(self):
        invalid_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-user': self.testuser.pk,
            'form-0-character': self.testcharacter.pk,
            'form-0-role': 'Krab',
            'form-0-site_count': '1',
            'form-1-user': self.testuser.pk,
            'form-1-character': self.testcharacter.pk,
            'form-1-role': 'Krab',
            'form-1-site_count': '1'
        }

        new_share_form = NewShareFormSet(invalid_data)

        roles_choices = [('Krab', 'Krab')]
        for form in new_share_form:
            form.fields['role'].choices = roles_choices

        self.assertFalse(new_share_form.is_valid())

    def test_ownership_invalid(self):
        invalid_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-user': self.testuser.pk,
            'form-0-character': self.testcharacter2.pk,
            'form-0-role': 'Krab',
            'form-0-site_count': '1',
            'form-1-user': self.testuser2.pk,
            'form-1-character': self.testcharacter.pk,
            'form-1-role': 'Krab',
            'form-1-site_count': '1'
        }

        new_share_form = NewShareFormSet(invalid_data)

        roles_choices = [('Krab', 'Krab')]
        for form in new_share_form:
            form.fields['role'].choices = roles_choices

        self.assertFalse(new_share_form.is_valid())

    def test_site_count_invalid(self):
        invalid_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-user': self.testuser.pk,
            'form-0-character': self.testcharacter.pk,
            'form-0-role': 'Krab',
            'form-0-site_count': '1',
            'form-1-user': self.testuser2.pk,
            'form-1-character': self.testcharacter2.pk,
            'form-1-role': 'Krab',
            'form-1-site_count': '-1'
        }

        new_share_form = NewShareFormSet(invalid_data)

        roles_choices = [('Krab', 'Krab')]
        for form in new_share_form:
            form.fields['role'].choices = roles_choices

        self.assertFalse(new_share_form.is_valid())
