from django.conf import settings
from ninja import NinjaAPI

from allianceauth_pve.models import PveButton, RoleSetup

from .activity import router as activity_router
from .authenticators import CanAccessPVE
from .permissions import router as permissions_router
from .projects import router as projects_router
from .rotations import router as rotations_router
from .schema import BaseRoleSetupSchema, PveButtonSchema
from .search import router as search_router

api = NinjaAPI(
    title="AA PvE API",
    version="0.0.1",
    urls_namespace="allianceauth_pve:api",
    auth=CanAccessPVE(),
    openapi_url=(settings.DEBUG and "/openapi.json") or "",
)

api.add_router("/rotations", rotations_router)
api.add_router("/activity", activity_router)
api.add_router("/projects", projects_router)
api.add_router("/permissions", permissions_router)
api.add_router("/search", search_router)


@api.get("/buttons/", response=list[PveButtonSchema])
def list_buttons(request):  # noqa: ARG001
    return PveButton.objects.all()


@api.get("/role_setups/", response=list[BaseRoleSetupSchema])
def list_role_setups(request):  # noqa: ARG001
    return RoleSetup.objects.all()
