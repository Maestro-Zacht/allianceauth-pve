from ninja import Path, Router

from django.db.models import F, Subquery, Sum, Prefetch
from django.utils.translation import gettext as _
from django.db import transaction
from django.core.cache import cache

from ..models import EntryLootItem, EntryRole, Rotation, Entry, EntryCharacter
from .schema import (
    EntrySchema,
    EntryRoleSchema,
    EntryCharacterSchema,
    EntryDetailsSchema,
    EntryFormSchema,
    EntryFormErrorsSchema,
    ExtendedEntryFormSchema,
    ExtendedEntryItemSchema,
)
from .authenticators import NeedsPermission
from ..app_settings import (
    ROTATION_SUMMARY_CACHE_KEY,
    ROTATION_PROJECT_SUMMARY_CACHE_KEY,
    FUNDING_PROJECT_SUMMARY_CACHE_KEY,
)

router = Router(tags=["entries"])


@router.get("/", response={200: list[EntrySchema], 404: None})
def get_rotation_entries(request, rotation_id: int = Path(...)):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, None

    return 200, (
        rotation.entries
        .with_items_total()
        .select_related('created_by__profile__main_character')
        .order_by('-created_at')
    )


@router.get("/{int:entry_id}/", response={200: EntryDetailsSchema, 404: None})
def get_rotation_entry(request, entry_id: int, rotation_id: int = Path(...)):
    try:
        entry = (
            Entry.objects
            .select_related(
                'created_by__profile__main_character',
                'funding_project',
                'rotation'
            )
            .with_items_total()
            .get(pk=entry_id, rotation_id=rotation_id)
        )
        return 200, entry
    except Entry.DoesNotExist:
        return 404, None


@router.delete(
    "/{int:entry_id}/",
    response={200: None, 403: str, 404: None},
    auth=NeedsPermission('allianceauth_pve.manage_entries')
)
def delete_rotation_entry(request, entry_id: int, rotation_id: int = Path(...)):
    try:
        entry = (
            Entry.objects
            .select_related('created_by', 'rotation')
            .get(pk=entry_id, rotation_id=rotation_id)
        )
    except Entry.DoesNotExist:
        return 404, None

    if (entry.created_by != request.user and not request.user.is_superuser) or entry.rotation.is_closed:
        return 403, "You cannot delete this entry"

    rotation_summary_cache_key = ROTATION_SUMMARY_CACHE_KEY.format(rotation_id=rotation_id)
    rotation_project_summary_cache_key = ROTATION_PROJECT_SUMMARY_CACHE_KEY.format(rotation_id=rotation_id)
    funding_project_summary_cache_key = None
    if entry.funding_project is not None:
        funding_project_summary_cache_key = FUNDING_PROJECT_SUMMARY_CACHE_KEY.format(project_id=entry.funding_project_id)

    entry.delete()

    cache.delete(rotation_summary_cache_key)

    if funding_project_summary_cache_key:
        cache.delete(rotation_project_summary_cache_key)
        cache.delete(funding_project_summary_cache_key)

    return 200, None


@router.get("/{int:entry_id}/roles/", response={200: list[EntryRoleSchema], 404: None})
def get_rotation_entry_roles(request, entry_id: int, rotation_id: int = Path(...)):
    try:
        entry = Entry.objects.get(pk=entry_id, rotation_id=rotation_id)
    except Entry.DoesNotExist:
        return 404, None

    total_value_qs = (
        EntryRole.objects
        .filter(entry_id=entry_id)
        .values('entry')
        .annotate(total=Sum('value'))
        .values('total')
    )

    return 200, entry.roles.annotate(
        role_approximate_percentage=F('value') * 100.0 / Subquery(total_value_qs)
    )


@router.get("/{int:entry_id}/shares/", response={200: list[EntryCharacterSchema], 404: None})
def get_rotation_entry_shares(request, entry_id: int, rotation_id: int = Path(...)):
    try:
        entry = Entry.objects.get(pk=entry_id, rotation_id=rotation_id)
    except Entry.DoesNotExist:
        return 404, None

    return 200, (
        entry.ratting_shares
        .select_related(
            'user__profile__main_character',
            'user_character',
            'role'
        )
        .with_totals()
    )


@router.get("/{int:entry_id}/items/", response={200: list[ExtendedEntryItemSchema], 404: None})
def get_rotation_entry_items(request, entry_id: int, rotation_id: int = Path(...)):
    try:
        entry = Entry.objects.get(pk=entry_id, rotation_id=rotation_id)
    except Entry.DoesNotExist:
        return 404, None

    items = (
        EntryLootItem.objects
        .filter(entry=entry)
        .select_related('item')
        .annotate(total_after_tax=(
            F('quantity') * F('sale_price') *
            (100.0 - F('entry__rotation__tax_rate_loot_items')) / 100.0
        ))
    )
    return 200, [{
        'id': item.item_id,
        'quantity': item.quantity,
        'name': item.item.name,
        'sale_price': item.sale_price,
        'total_after_tax': item.total_after_tax
    } for item in items]


@router.post(
    "/",
    response={200: None, 400: EntryFormErrorsSchema, 404: None, 403: str},
    auth=NeedsPermission('allianceauth_pve.manage_entries')
)
def new_entry(request, data: EntryFormSchema, rotation_id: int = Path(...)):
    with transaction.atomic():
        try:
            rotation = Rotation.objects.get(pk=rotation_id)
        except Rotation.DoesNotExist:
            return 404, None

        if rotation.is_closed:
            return 403, _("The rotation is closed")

        errors = data.validate()
        if errors is not None:
            return 400, errors

        entry = data.save(request.user, rotation)

    rotation_summary_cache_key = ROTATION_SUMMARY_CACHE_KEY.format(rotation_id=rotation_id)
    rotation_project_summary_cache_key = ROTATION_PROJECT_SUMMARY_CACHE_KEY.format(rotation_id=rotation_id)

    cache.delete(rotation_summary_cache_key)

    if entry.funding_project is not None:
        cache.delete(rotation_project_summary_cache_key)

        funding_project_summary_cache_key = FUNDING_PROJECT_SUMMARY_CACHE_KEY.format(project_id=entry.funding_project_id)
        cache.delete(funding_project_summary_cache_key)

    return 200, None


@router.get(
    "/{int:entry_id}/edit/",
    response={200: ExtendedEntryFormSchema, 404: None, 403: str},
    auth=NeedsPermission('allianceauth_pve.manage_entries')
)
def get_entry_for_edit(request, entry_id: int, rotation_id: int = Path(...)):
    try:
        entry_char_qs = EntryCharacter.objects.select_related('user_character', 'role', 'user__profile__main_character')
        entry = (
            Entry.objects
            .select_related('rotation')
            .prefetch_related(Prefetch('ratting_shares', queryset=entry_char_qs, to_attr='shares'))
            .get(pk=entry_id, rotation_id=rotation_id)
        )
    except Entry.DoesNotExist:
        return 404, None

    if entry.created_by != request.user and not request.user.is_superuser:
        return 403, _("You cannot edit this entry")

    if entry.rotation.is_closed:
        return 403, _("The rotation is closed")

    if EntryCharacter.objects.filter(entry=entry, user__profile__main_character__isnull=True).exists():
        return 403, _("One or more characters in this entry do not have a main character set")

    return 200, entry


@router.post(
    "/{int:entry_id}/",
    response={200: None, 400: EntryFormErrorsSchema, 404: None, 403: str},
    auth=NeedsPermission('allianceauth_pve.manage_entries')
)
def edit_entry(request, entry_id: int, data: EntryFormSchema, rotation_id: int = Path(...)):
    with transaction.atomic():
        try:
            entry = Entry.objects.select_related('rotation').get(pk=entry_id, rotation_id=rotation_id)
        except Entry.DoesNotExist:
            return 404, None

        if entry.created_by != request.user and not request.user.is_superuser:
            return 403, _("You cannot edit this entry")

        if entry.rotation.is_closed:
            return 403, _("The rotation is closed")

        errors = data.validate()
        if errors is not None:
            return 400, errors

        rotation_summary_cache_key = ROTATION_SUMMARY_CACHE_KEY.format(rotation_id=rotation_id)
        rotation_project_summary_cache_key = ROTATION_PROJECT_SUMMARY_CACHE_KEY.format(rotation_id=rotation_id)
        funding_project_summary_cache_keys = set()
        if entry.funding_project is not None:
            funding_project_summary_cache_keys.add(
                FUNDING_PROJECT_SUMMARY_CACHE_KEY.format(project_id=entry.funding_project_id)
            )

        new_entry = data.save(request.user, entry.rotation, entry)

        if new_entry.funding_project is not None:
            funding_project_summary_cache_keys.add(
                FUNDING_PROJECT_SUMMARY_CACHE_KEY.format(project_id=new_entry.funding_project_id)
            )

    cache.delete(rotation_summary_cache_key)

    if len(funding_project_summary_cache_keys) > 0:
        cache.delete(rotation_project_summary_cache_key)
        cache.delete_many(funding_project_summary_cache_keys)

    return 200, None
