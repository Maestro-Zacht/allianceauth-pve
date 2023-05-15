from django.test import SimpleTestCase, TestCase
from django.template import Context, Template

from allianceauth.tests.auth_utils import AuthUtils

from allianceauth_pve import __version__


class TestGetMainCharacterFilter(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.template = Template('{% load pvefilters %}{{ user|get_main_character }}')

    def test_user_success(self):
        context = Context({'user': self.testuser})

        res = self.template.render(context)

        self.assertEqual(res, 'aauth_testchar')

    def test_int_success(self):
        context = Context({'user': self.testuser.pk})

        res = self.template.render(context)

        self.assertEqual(res, 'aauth_testchar')

    def test_int_fail(self):
        context = Context({'user': self.testuser.pk + 10})

        res = self.template.render(context)

        self.assertEqual(res, '')

    def test_str_not_valid(self):
        context = Context({'user': 'not valid param'})

        res = self.template.render(context)

        self.assertEqual(res, '')

    def test_valid_str(self):
        context = Context({'user': str(self.testuser.pk)})

        res = self.template.render(context)

        self.assertEqual(res, 'aauth_testchar')

    def test_param_not_valid(self):
        context = Context({'user': []})

        res = self.template.render(context)

        self.assertEqual(res, '')


class TestGetCharAttrFilter(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser = AuthUtils.create_user('aauth_testuser')
        cls.testcharacter = AuthUtils.add_main_character_2(cls.testuser, 'aauth_testchar', 2116790529)

        cls.template = Template('{% load pvefilters %}{{ char|get_char_attr:"character_name" }}')

    def test_character_success(self):
        context = Context({'char': self.testcharacter})

        res = self.template.render(context)

        self.assertEqual(res, self.testcharacter.character_name)

    def test_int_success(self):
        context = Context({'char': self.testcharacter.pk})

        res = self.template.render(context)

        self.assertEqual(res, self.testcharacter.character_name)

    def test_int_fail(self):
        context = Context({'char': self.testcharacter.pk + 10})

        res = self.template.render(context)

        self.assertEqual(res, '')

    def test_str_fail(self):
        context = Context({'char': 'notanumber'})

        res = self.template.render(context)

        self.assertEqual(res, '')

    def test_str_success(self):
        context = Context({'char': str(self.testcharacter.pk)})

        res = self.template.render(context)

        self.assertEqual(res, self.testcharacter.character_name)

    def test_param_not_valid(self):
        context = Context({'char': []})

        res = self.template.render(context)

        self.assertEqual(res, '')


class TestPvEVersionedStatic(SimpleTestCase):
    """
    Tests for allianceauth_pve_versioned_static template tag
    """

    def test_versioned_static(self):
        """
        Test should return static URL string with version
        :return:
        """

        context = Context({"version": __version__})
        template_to_render = Template(
            "{% load allianceauth_pve_versioned_static %}"
            "{% allianceauth_pve_static 'allianceauth_pve/css/custom_checkbox.css' %}"
        )

        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            f'/static/allianceauth_pve/css/custom_checkbox.css?v={context["version"]}',
            rendered_template,
        )
