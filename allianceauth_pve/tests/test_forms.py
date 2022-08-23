from django.test import SimpleTestCase

from ..forms import NewRoleFormSet


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

    def test_invalid(self):
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

        role_form = NewRoleFormSet(invalid_data)

        self.assertFalse(role_form.is_valid())
