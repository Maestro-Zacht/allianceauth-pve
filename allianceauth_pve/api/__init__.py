from ninja import NinjaAPI

from django.conf import settings

from .rotations import router as rotations_router
from .activity import router as activity_router
from .projects import router as projects_router
from .permissions import router as permissions_router

from .authenticators import CanAccessPVE


api = NinjaAPI(
    title="AA PvE API",
    version="0.0.1",
    urls_namespace='allianceauth_pve:api',
    auth=CanAccessPVE(),
    openapi_url=settings.DEBUG and "/openapi.json" or ""
)

api.add_router("/rotations", rotations_router)
api.add_router("/activity", activity_router)
api.add_router("/projects", projects_router)
api.add_router("/permissions", permissions_router)
