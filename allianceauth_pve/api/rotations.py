from ninja import Router

from django.db.models import Count, F
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.utils import timezone

from ..models import Rotation
from .schema import (
    RotationSchema,
    RotationSummarySchema,
    RotationProjectSummarySchema,
    NewRotationSchema,
    CloseRotationSchema
)
from .authenticators import NeedsPermission
from ..utils import ensure_rotation_presets_applied

from .entries import router as entries_router

router = Router(tags=["rotations"])
router.add_router("/{int:rotation_id}/entries", entries_router)


@router.get("/", response=list[RotationSchema])
def list_rotations(request):
    return Rotation.objects.annotate(
        number_of_members=Count(
            'entries__ratting_shares__user',
            distinct=True
        )
    )


@router.post("/", response={200: int, 400: dict[str, list[str]]}, auth=NeedsPermission('allianceauth_pve.manage_rotations'))
def create_rotation(request, data: NewRotationSchema):
    errors = data.validate()
    if errors:
        return 400, errors

    rotation = Rotation.objects.create(
        name=data.name,
        priority=data.priority,
        tax_rate=data.tax_rate,
        max_daily_setups=data.max_daily_setups,
        min_people_share_setup=data.min_people_share_setup
    )
    rotation.entry_buttons.set(data.entry_buttons)
    rotation.roles_setups.set(data.roles_setups)

    return 200, rotation.pk


@router.get("/{int:rotation_id}/", response={200: RotationSchema, 404: None})
def get_rotation(request, rotation_id: int):
    try:
        return 200, Rotation.objects.annotate(
            number_of_members=Count(
                'entries__ratting_shares__user',
                distinct=True
            )
        ).get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, None


@router.patch(
    "/{int:rotation_id}/",
    response={200: None, 400: dict[str, list[str]], 403: None, 404: None},
    auth=NeedsPermission('allianceauth_pve.manage_rotations')
)
def close_rotation(request, rotation_id: int, data: CloseRotationSchema):
    user: User = request.user

    errors = data.validate()
    if errors:
        return 400, errors

    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, None

    if rotation.is_closed or not user.has_perm('allianceauth_pve.manage_rotations'):
        return 403, None

    rotation.actual_total = data.sales_value
    rotation.is_closed = True
    rotation.closed_at = timezone.now()
    rotation.save(update_fields=['actual_total', 'is_closed', 'closed_at'])

    # TODO: cache invalidation

    ensure_rotation_presets_applied()

    return 200, None


@router.get("/{int:rotation_id}/summary/", response={200: list[RotationSummarySchema], 404: None})
def get_rotation_summary(request, rotation_id: int):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, None

    return 200, rotation.summary.order_by('-estimated_total').values(
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
        main_character_id=F('user__profile__main_character__character_id'),
    )


@router.get("/{int:rotation_id}/project_summaries/", response={200: list[RotationProjectSummarySchema], 404: None})
def get_rotation_project_summaries(request, rotation_id: int):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, None

    return 200, [
        {'project': project, 'summary': summary}
        for project, summary in rotation.funding_projects_summary.items()
    ]
