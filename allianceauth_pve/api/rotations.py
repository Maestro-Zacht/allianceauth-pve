from ninja import Router

from django.db.models import Count, F, Subquery, Sum
from django.db.models.functions import Coalesce

from ..models import EntryRole, Rotation, Entry
from .schema import RotationSchema, RotationSummarySchema, ProjectSummarySchema, EntrySchema, EntryRoleSchema, EntryCharacterSchema, EntryDetailsSchema
from .authenticators import NeedsPermission

router = Router(tags=["rotations"])


@router.get("/", response=list[RotationSchema])
def list_rotations(request):
    return Rotation.objects.annotate(
        number_of_members=Count(
            'entries__ratting_shares__user',
            distinct=True
        )
    )


@router.get("/{int:rotation_id}/", response={200: RotationSchema, 404: str})
def get_rotation(request, rotation_id: int):
    try:
        return 200, Rotation.objects.annotate(
            number_of_members=Count(
                'entries__ratting_shares__user',
                distinct=True
            )
        ).get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, "Rotation not found"


@router.get("/{int:rotation_id}/summary/", response={200: list[RotationSummarySchema], 404: str})
def get_rotation_summary(request, rotation_id: int):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, "Rotation not found"

    return 200, rotation.summary.order_by('-estimated_total').values(
        'user',
        'helped_setups',
        'estimated_total',
        'actual_total',
        character_name=Coalesce(
            F('user__profile__main_character__character_name'),
            F('user_character__character_name'),
        ),
        character_id=Coalesce(
            F('user__profile__main_character__character_id'),
            F('user_character__character_id'),
        ),
    )


@router.get("/{int:rotation_id}/project_summaries/", response={200: list[ProjectSummarySchema], 404: str})
def get_rotation_project_summaries(request, rotation_id: int):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, "Rotation not found"

    return 200, [
        {'project': project, 'summary': summary}
        for project, summary in rotation.funding_projects_summary.items()
    ]


@router.get("/{int:rotation_id}/entries/", response={200: list[EntrySchema], 404: str})
def get_rotation_entries(request, rotation_id: int):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, "Rotation not found"

    return 200, (
        rotation.entries
        .select_related('created_by__profile__main_character')
        .order_by('-created_at')
    )


@router.get("/{int:rotation_id}/entries/{int:entry_id}/", response={200: EntryDetailsSchema, 404: str})
def get_rotation_entry(request, rotation_id: int, entry_id: int):
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
        return 404, "Entry not found"


@router.delete(
    "/{int:rotation_id}/entries/{int:entry_id}/",
    response={200: None, 403: str, 404: str},
    auth=NeedsPermission('allianceauth_pve.manage_entries')
)
def delete_rotation_entry(request, rotation_id: int, entry_id: int):
    try:
        entry = (
            Entry.objects
            .select_related('created_by', 'rotation')
            .get(pk=entry_id, rotation_id=rotation_id)
        )
    except Entry.DoesNotExist:
        return 404, "Entry not found"

    if (entry.created_by != request.user and not request.user.is_superuser) or entry.rotation.is_closed:
        return 403, "You cannot delete this entry"

    entry.delete()

    return 200, None


@router.get("/{int:rotation_id}/entries/{int:entry_id}/roles/", response={200: list[EntryRoleSchema], 404: str})
def get_rotation_entry_roles(request, rotation_id: int, entry_id: int):
    try:
        entry = Entry.objects.get(pk=entry_id, rotation_id=rotation_id)
    except Entry.DoesNotExist:
        return 404, "Entry not found"

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


@router.get("/{int:rotation_id}/entries/{int:entry_id}/shares/", response={200: list[EntryCharacterSchema], 404: str})
def get_rotation_entry_shares(request, rotation_id: int, entry_id: int):
    try:
        entry = Entry.objects.get(pk=entry_id, rotation_id=rotation_id)
    except Entry.DoesNotExist:
        return 404, "Entry not found"

    return 200, (
        entry.ratting_shares
        .select_related(
            'user__profile__main_character',
            'user_character',
            'role'
        )
        .with_totals()
    )
