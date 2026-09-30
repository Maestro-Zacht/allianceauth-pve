# Django
from django.urls import path
from django.urls import include

# Alliance Auth
from allianceauth import urls

urlpatterns = [
    # Alliance Auth URLs
    path("", include(urls)),
]
