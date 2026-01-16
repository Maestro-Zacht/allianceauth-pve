from ninja import Router

from django.db.models import Count, F
from django.db.models.functions import Coalesce

from ..models import Rotation
from .schema import RotationSchema, RotationSummarySchema, ProjectSummarySchema, EntrySchema

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
