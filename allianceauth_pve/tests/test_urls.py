from django.test import SimpleTestCase
from django.urls import resolve, reverse

from .. import views


class TestUrls(SimpleTestCase):

    def test_index_url(self):
        url = reverse('allianceauth_pve:index')
        self.assertEqual(resolve(url).func.__name__, views.index.__name__)
        self.assertEqual(resolve(url).func.__module__, views.index.__module__)

    def test_dashboard_url(self):
        url = reverse('allianceauth_pve:dashboard')
        self.assertEqual(resolve(url).func.__name__, views.dashboard.__name__)
        self.assertEqual(resolve(url).func.__module__, views.dashboard.__module__)

    def test_new_rotation_url(self):
        url = reverse('allianceauth_pve:new_rotation')
        self.assertEqual(resolve(url).func.__name__, views.create_rotation.__name__)
        self.assertEqual(resolve(url).func.__module__, views.create_rotation.__module__)

    def test_rotation_view_url(self):
        url = reverse('allianceauth_pve:rotation_view', args=[1])
        self.assertEqual(resolve(url).func.__name__, views.rotation_view.__name__)
        self.assertEqual(resolve(url).func.__module__, views.rotation_view.__module__)

    def test_new_entry_url(self):
        url = reverse('allianceauth_pve:new_entry', args=[1])
        self.assertEqual(resolve(url).func.__name__, views.add_entry.__name__)
        self.assertEqual(resolve(url).func.__module__, views.add_entry.__module__)

    def test_edit_entry_url(self):
        url = reverse('allianceauth_pve:edit_entry', args=[1, 1])
        self.assertEqual(resolve(url).func.__name__, views.add_entry.__name__)
        self.assertEqual(resolve(url).func.__module__, views.add_entry.__module__)

    def test_entry_detail_url(self):
        url = reverse('allianceauth_pve:entry_detail', args=[1])
        self.assertEqual(resolve(url).func.view_class, views.EntryDetailView)

    def test_delete_entry_url(self):
        url = reverse('allianceauth_pve:delete_entry', args=[1])
        self.assertEqual(resolve(url).func.__name__, views.delete_entry.__name__)
        self.assertEqual(resolve(url).func.__module__, views.delete_entry.__module__)

    def test_all_ratters_url(self):
        url = reverse('allianceauth_pve:all_ratters')
        self.assertEqual(resolve(url).func.__name__, views.get_avaiable_ratters.__name__)
        self.assertEqual(resolve(url).func.__module__, views.get_avaiable_ratters.__module__)

    def test_search_ratters_url(self):
        url = reverse('allianceauth_pve:search_ratters', args=['Maestro'])
        self.assertEqual(resolve(url).func.__name__, views.get_avaiable_ratters.__name__)
        self.assertEqual(resolve(url).func.__module__, views.get_avaiable_ratters.__module__)
