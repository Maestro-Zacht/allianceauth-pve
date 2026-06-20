from django.apps import AppConfig

from . import __version__


class AllianceauthPveConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "allianceauth_pve"
    verbose_name = f"AllianceAuth PvE {__version__}"

    def ready(self):
        from . import checks  # noqa: F401, PLC0415
