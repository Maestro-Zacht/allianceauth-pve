from django.urls import path, re_path

from . import views
from .api import api

app_name = "allianceauth_pve"


urlpatterns = [
    path("", views.index, name="index"),
    path("api/", api.urls),
    re_path("^r/", views.react_view, name="react_view"),
]
