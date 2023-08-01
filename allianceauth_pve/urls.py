from django.urls import path

from . import views

app_name = 'allianceauth_pve'


urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('rotation/new/', views.create_rotation, name='new_rotation'),
    path('rotation/<int:rotation_id>/', views.rotation_view, name='rotation_view'),
    path('rotation/<int:rotation_id>/entryform/', views.add_entry, name='new_entry'),
    path('rotation/<int:rotation_id>/entryform/<int:entry_id>/', views.add_entry, name='edit_entry'),
    path('entry/<int:pk>/', views.EntryDetailView.as_view(), name="entry_detail"),
    path('entry/<int:entry_id>/delete/', views.delete_entry, name='delete_entry'),
    path('ratters/', views.get_avaiable_ratters, name='all_ratters'),
    path('ratters/<str:name>/', views.get_avaiable_ratters, name='search_ratters'),
    path('project/new/', views.new_project_view, name='new_project'),
    path('project/<int:pk>/', views.FundingProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/complete', views.toggle_complete_project, name='project_toggle_complete'),
]
