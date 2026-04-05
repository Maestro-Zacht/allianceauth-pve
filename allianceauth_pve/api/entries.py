from ninja import Path, Router

from django.db.models import F, Subquery, Sum
from django.utils.translation import gettext as _
from django.db import transaction

from ..models import EntryRole, Rotation, Entry
from .schema import (
    EntrySchema,
    EntryRoleSchema,
    EntryCharacterSchema,
    EntryDetailsSchema,
    EntryFormSchema
)
from .authenticators import NeedsPermission

router = Router(tags=["entries"])


@router.get("/", response={200: list[EntrySchema], 404: None})
def get_rotation_entries(request, rotation_id: int = Path(...)):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, None

    return 200, (
        rotation.entries
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

    entry.delete()

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


@router.post(
    "/",
    response={200: None, 400: dict[str, list[str] | dict[int, dict[str, list[str]]]], 404: None, 403: str},
    auth=NeedsPermission('allianceauth_pve.manage_entries')
)
@transaction.atomic
def new_entry(request, data: EntryFormSchema, rotation_id: int = Path(...)):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, None

    if rotation.is_closed:
        return 403, _("The rotation is closed, you cannot add an entry")

    errors = data.validate()
    if errors:
        return 400, errors

    data.save(created_by=request.user, rotation=rotation)

    # TODO: cache keys

    return 200, None
