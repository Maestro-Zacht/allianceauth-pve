from django.urls import path

from . import views

app_name = 'allianceauth_pve'


urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('rotation/<int:rotation_id>/', views.rotation_view, name='rotation_view'),
    path('rotation/<int:rotation_id>/newentry/', views.add_entry, name='new_entry'),
    path('entry/<int:pk>/', views.EntryDetailView.as_view(), name="entry_detail"),
]
