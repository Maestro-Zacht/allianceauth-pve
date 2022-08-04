from django.test import SimpleTestCase
from django.urls import resolve, reverse

from .. import views


class TestUrls(SimpleTestCase):

    def test_index_url(self):
        url = reverse('allianceauth_pve:index')
        self.assertEqual(resolve(url).func, views.index)

    def test_dashboard_url(self):
        url = reverse('allianceauth_pve:dashboard')
        self.assertEqual(resolve(url).func, views.dashboard)

    def test_new_rotation_url(self):
        url = reverse('allianceauth_pve:new_rotation')
        self.assertEqual(resolve(url).func, views.create_rotation)

    def test_rotation_view_url(self):
        url = reverse('allianceauth_pve:rotation_view', args=[1])
        self.assertEqual(resolve(url).func, views.rotation_view)

    def test_new_entry_url(self):
        url = reverse('allianceauth_pve:new_entry', args=[1])
        self.assertEqual(resolve(url).func, views.add_entry)

    def test_edit_entry_url(self):
        url = reverse('allianceauth_pve:edit_entry', args=[1, 1])
        self.assertEqual(resolve(url).func, views.add_entry)

    def test_entry_detail_url(self):
        url = reverse('allianceauth_pve:entry_detail', args=[1])
        self.assertEqual(resolve(url).func.view_class, views.EntryDetailView)

    def test_delete_entry_url(self):
        url = reverse('allianceauth_pve:delete_entry', args=[1])
        self.assertEqual(resolve(url).func, views.delete_entry)

    def test_all_ratters_url(self):
        url = reverse('allianceauth_pve:all_ratters')
        self.assertEqual(resolve(url).func, views.get_avaiable_ratters)

    def test_search_ratters_url(self):
        url = reverse('allianceauth_pve:search_ratters', args=['Maestro'])
        self.assertEqual(resolve(url).func, views.get_avaiable_ratters)
