from django.test import SimpleTestCase, TestCase
from django.template import Context, Template

from allianceauth_pve import __version__


class TestPvEVersionedStatic(TestCase):
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
