from django.test import TestCase, override_settings

from allianceauth_pve.checks import check_settings


class TestCheckSettings(TestCase):
    @override_settings(
        PVE_ONLY_MAINS=True,
        PVE_IGNORED_ITEM_GROUPS=[1, 2],
        PVE_IGNORED_ITEM_IDS=[3],
    )
    def test_valid_settings(self):
        self.assertEqual(check_settings(None), [])

    @override_settings(PVE_ONLY_MAINS="yes")
    def test_only_mains_wrong_type(self):
        errors = check_settings(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "allianceauth_pve.E001")

    @override_settings(PVE_IGNORED_ITEM_GROUPS=[1, "a"])
    def test_ignored_item_groups_wrong_element_type(self):
        errors = check_settings(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "allianceauth_pve.E002")

    @override_settings(PVE_IGNORED_ITEM_GROUPS="not-a-list")
    def test_ignored_item_groups_not_a_list(self):
        errors = check_settings(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "allianceauth_pve.E002")

    @override_settings(PVE_IGNORED_ITEM_IDS=[1, None])
    def test_ignored_item_ids_wrong_element_type(self):
        errors = check_settings(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "allianceauth_pve.E003")

    @override_settings(
        PVE_ONLY_MAINS=1,
        PVE_IGNORED_ITEM_GROUPS="nope",
        PVE_IGNORED_ITEM_IDS="nope",
    )
    def test_all_invalid(self):
        errors = check_settings(None)
        self.assertEqual(
            [error.id for error in errors],
            [
                "allianceauth_pve.E001",
                "allianceauth_pve.E002",
                "allianceauth_pve.E003",
            ],
        )
