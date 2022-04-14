from django.urls import path

from . import views

app_name = 'allianceauth_pve'


urlpatterns = [
    path('rotation/<int:rotation_id>/', views.rotation_view, name='rotation_view')
]
