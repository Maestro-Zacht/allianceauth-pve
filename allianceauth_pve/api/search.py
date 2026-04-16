from collections import defaultdict

from ninja import Router, Body

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Exists, OuterRef, F, Prefetch

from allianceauth.authentication.models import CharacterOwnership

from eve_sde.models import ItemType

from ..models import General
from ..app_settings import PVE_ONLY_MAINS
from ..utils import parse_items_from_inventory
from .schema import RatterSchema, ItemSearchResultSchema
from .authenticators import NeedsPermission

router = Router(tags=["search"])


@router.post(
    "/ratters/",
    response=list[RatterSchema],
    auth=NeedsPermission('allianceauth_pve.manage_entries')
)
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


@router.post(
    "/items/",
    response={200: list[ItemSearchResultSchema], 400: list[str]},
    auth=NeedsPermission('allianceauth_pve.manage_entries')
)
def search_items(request, paste: str = Body(...)):
    items = defaultdict(int)
    no_match = []

    for line in paste.splitlines():
        parsed = parse_items_from_inventory(line)
        if parsed is not None:
            name, quantity = parsed
            items[name] += quantity
        else:
            no_match.append(line)

    if len(no_match) > 0:
        return 400, no_match

    item_objs: list[ItemType] = []
    for item in ItemType.objects.filter(name__in=items.keys(), published=True):
        item.quantity = items[item.name]
        item_objs.append(item)

    if len(item_objs) != len(items):
        missing_items = set(items.keys()) - set(item.name for item in item_objs)
        return 400, list(missing_items)

    return 200, item_objs
