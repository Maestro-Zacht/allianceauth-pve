from allianceauth import hooks
from allianceauth.services.hooks import UrlHook, MenuItemHook
from allianceauth.services.hooks import get_extension_logger

from . import urls

logger = get_extension_logger(__name__)


class PveMenuItemHook(MenuItemHook):
    def __init__(self):
        super().__init__("PvE Tool", "fas fa-wallet", "allianceauth_pve:index", navactive=['allianceauth_pve:'])

    def render(self, request):
        if request.user.has_perm('allianceauth_pve.access_pve'):
            logger.debug(f"User {request.user} allowed to access pve.")
            return super().render(request)
        logger.debug(f"User {request.user} not allowed to access pve.")
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return PveMenuItemHook()


@hooks.register('url_hook')
def register_urls():
    return UrlHook(urls, 'allianceauth_pve', 'pve/')
