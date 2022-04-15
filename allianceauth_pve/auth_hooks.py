from allianceauth import hooks
from allianceauth.services.hooks import UrlHook, MenuItemHook

from . import urls


class PveMenuItemHook(MenuItemHook):
    def __init__(self):
        super().__init__("PvE Tool", "fas fa-wallet", "allianceauth_pve:index", navactive=['allianceauth_pve:'])


@hooks.register('menu_item_hook')
def register_menu():
    return PveMenuItemHook()


@hooks.register('url_hook')
def register_urls():
    return UrlHook(urls, 'allianceauth_pve', 'pve/')
