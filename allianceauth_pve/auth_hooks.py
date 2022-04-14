from allianceauth import hooks
from allianceauth.services.hooks import UrlHook

from . import urls


@hooks.register('url_hook')
def register_urls():
    return UrlHook(urls, 'allianceauth_pve', 'pve/')
