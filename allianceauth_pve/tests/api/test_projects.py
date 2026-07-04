from unittest import mock

from django.core.cache import cache

from allianceauth_pve.app_settings import FUNDING_PROJECT_SUMMARY_CACHE_KEY
from allianceauth_pve.models import FundingProject
from allianceauth_pve.tests.utils import (
    ACCESS,
    MANAGE_ENTRIES,
    MANAGE_PROJECTS,
    PveApiTestBase,
    url,
)


class TestProjectsApi(PveApiTestBase):
    @classmethod
    def setUpTestData(cls):
        cls.user, cls.char = cls.make_user(
            "proj_user",
            90600001,
            "ProjUser",
            perms=[ACCESS, MANAGE_PROJECTS, MANAGE_ENTRIES],
        )
        cls.active = FundingProject.objects.create(name="active_proj", goal=1_000_000)
        cls.inactive = FundingProject.objects.create(
            name="done_proj", goal=1_000_000, is_active=False
        )

    def test_list_projects_all(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("list_projects"))
        self.assertEqual(resp.status_code, 200)
        ids = {p["id"] for p in resp.json()}
        self.assertSetEqual({self.active.pk, self.inactive.pk}, ids)

    def test_list_projects_active(self):
        self.client.force_login(self.user)
        data = self.client.get(url("list_projects") + "?active=true").json()
        ids = {p["id"] for p in data}
        self.assertSetEqual({self.active.pk}, ids)
        self.assertIn("number_of_participants", data[0])

    def test_list_projects_inactive(self):
        self.client.force_login(self.user)
        data = self.client.get(url("list_projects") + "?active=false").json()
        ids = {p["id"] for p in data}
        self.assertSetEqual({self.inactive.pk}, ids)
        self.assertNotIn(self.active.pk, ids)

    def test_get_project(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("get_project", project_id=self.active.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], self.active.pk)

    def test_get_project_404(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("get_project", project_id=999999))
        self.assertEqual(resp.status_code, 404)

    def test_create_project_success(self):
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "create_project", {"name": "Fresh", "goal": 5_000_000}
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertTrue(FundingProject.objects.filter(pk=resp.json()).exists())

    def test_create_project_empty_name(self):
        self.client.force_login(self.user)
        resp = self.api_request("POST", "create_project", {"name": "", "goal": 1})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("name", resp.json())

    def test_create_project_long_name(self):
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "create_project", {"name": "x" * 129, "goal": 1}
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("name", resp.json())

    def test_create_project_duplicate_active_name(self):
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "create_project", {"name": "active_proj", "goal": 1}
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("name", resp.json())

    def test_create_project_bad_goal(self):
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "create_project", {"name": "GoalBad", "goal": 0}
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("goal", resp.json())

    def test_get_project_summary(self):
        rotation = self.make_rotation(name="projsumrot")
        self.make_entry(
            rotation,
            self.user,
            self.char,
            funding_project=self.active,
            funding_percentage=50,
        )
        self.client.force_login(self.user)
        target = url("get_project_summary", project_id=self.active.pk)
        resp = self.client.get(target)
        self.assertEqual(resp.status_code, 200)
        cache_key = FUNDING_PROJECT_SUMMARY_CACHE_KEY.format(project_id=self.active.pk)
        self.assertTrue(cache.has_key(cache_key))

        with mock.patch.object(cache, "get", wraps=cache.get) as mock_cache_get:
            resp2 = self.client.get(target)
            mock_cache_get.assert_called_with(cache_key)
            self.assertEqual(resp2.json(), resp.json())

    def test_get_project_summary_404(self):
        self.client.force_login(self.user)
        resp = self.client.get(url("get_project_summary", project_id=999999))
        self.assertEqual(resp.status_code, 404)

    def test_toggle_complete_project(self):
        project = FundingProject.objects.create(name="toggle_me", goal=1)
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "toggle_complete_project", project_id=project.pk
        )
        self.assertEqual(resp.status_code, 200)
        project.refresh_from_db()
        self.assertFalse(project.is_active)
        self.assertIsNotNone(project.completed_at)

        # reopen
        resp = self.api_request(
            "POST", "toggle_complete_project", project_id=project.pk
        )
        self.assertEqual(resp.status_code, 200)
        project.refresh_from_db()
        self.assertTrue(project.is_active)
        self.assertIsNone(project.completed_at)

    def test_toggle_complete_with_open_contributions(self):
        project = FundingProject.objects.create(name="open_contrib", goal=1)
        rotation = self.make_rotation(name="opencontribrot")  # open
        self.make_entry(
            rotation,
            self.user,
            self.char,
            funding_project=project,
            funding_percentage=50,
        )
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "toggle_complete_project", project_id=project.pk
        )
        self.assertEqual(resp.status_code, 403)

    def test_toggle_reopen_with_active_same_name(self):
        completed = FundingProject.objects.create(
            name=self.active.name, goal=1, is_active=False
        )
        self.client.force_login(self.user)
        resp = self.api_request(
            "POST", "toggle_complete_project", project_id=completed.pk
        )
        self.assertEqual(resp.status_code, 400)

    def test_toggle_complete_404(self):
        self.client.force_login(self.user)
        resp = self.api_request("POST", "toggle_complete_project", project_id=999999)
        self.assertEqual(resp.status_code, 404)
