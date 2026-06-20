from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook, get_extension_logger
from django.utils.translation import gettext_lazy as _

from . import urls

logger = get_extension_logger(__name__)


class PveMenuItemHook(MenuItemHook):
    def __init__(self):
        super().__init__(
            _("PvE Tool"),
            "fas fa-wallet",
            "allianceauth_pve:index",
            navactive=["allianceauth_pve:"],
        )

    def render(self, request):
        if request.user.has_perm("allianceauth_pve.access_pve"):
            return super().render(request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return PveMenuItemHook()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "allianceauth_pve", "pve/")
