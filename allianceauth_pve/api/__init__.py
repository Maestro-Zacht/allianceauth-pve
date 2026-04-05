from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Exists, OuterRef, F, Prefetch

from ninja import NinjaAPI

from django.conf import settings

from allianceauth.authentication.models import CharacterOwnership

from ..models import PveButton, RoleSetup, General
from ..app_settings import PVE_ONLY_MAINS
from .schema import PveButtonSchema, BaseRoleSetupSchema, RatterSchema

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


@api.get("/buttons/", response=list[PveButtonSchema])
def list_buttons(request):
    return PveButton.objects.all()


@api.get("/role_setups/", response=list[BaseRoleSetupSchema])
def list_role_setups(request):
    return RoleSetup.objects.all()


@api.post("/search/", response=list[RatterSchema])
def search_ratters(request, name: str = "", exclude_ids: list[int] = []):
    content_type = ContentType.objects.get_for_model(General)
    permission = Permission.objects.get(content_type=content_type, codename='access_pve')

    ownerships = CharacterOwnership.objects.filter(
        Q(user__groups__permissions=permission) |
        Q(user__user_permissions=permission) |
        Q(user__profile__state__permissions=permission),
        user__profile__main_character__isnull=False,
    )

    if name:
        alts_name = CharacterOwnership.objects.filter(
            user=OuterRef('user'),
            character__character_name__icontains=name
        )
        ownerships = ownerships.filter(
            Q(character__character_name__icontains=name) |
            (Exists(alts_name) & Q(character=F('user__profile__main_character')))
        )

    if exclude_ids:
        ownerships = ownerships.exclude(character__character_id__in=exclude_ids)

    if PVE_ONLY_MAINS:
        ownerships = ownerships.filter(character=F('user__profile__main_character'))

    alts_qs = (
        CharacterOwnership.objects
        .select_related('character')
        .exclude(character=F('user__profile__main_character'))
    )

    return 200, (
        ownerships
        .select_related('character', 'user__profile__main_character')
        .prefetch_related(Prefetch('user__character_ownerships', queryset=alts_qs, to_attr='alts'))
        .distinct()
    )
