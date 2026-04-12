from django.apps import AppConfig
from . import __version__


class AllianceauthPveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'allianceauth_pve'
    verbose_name = f"AllianceAuth PvE {__version__}"
