from ninja import Router

from django.db.models import Count, F, Sum
from django.db.models.functions import Coalesce
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache

from ..models import EntryCharacter, FundingProject, Rotation, EntryLootItem
from .schema import (
    RotationSchema,
    RotationSummarySchema,
    RotationProjectSummarySchema,
    NewRotationSchema,
    CloseRotationSchema,
    CloseRotationErrorsSchema,
    RoleSetupSchema,
    PveButtonSchema,
    ExtendedEntryItemSchema,
)
from .authenticators import NeedsPermission
from ..utils import ensure_rotation_presets_applied
from ..app_settings import (
    ROTATION_SUMMARY_CACHE_KEY,
    ROTATION_SUMMARY_CACHE_TIMEOUT,
    ROTATION_PROJECT_SUMMARY_CACHE_KEY,
    ROTATION_PROJECT_SUMMARY_CACHE_TIMEOUT,
    FUNDING_PROJECT_SUMMARY_CACHE_KEY,
    ACTIVITY_CACHE_KEY,
)

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
    response={200: None, 400: CloseRotationErrorsSchema, 403: None, 404: None},
    auth=NeedsPermission('allianceauth_pve.manage_rotations')
)
def close_rotation(request, rotation_id: int, data: CloseRotationSchema):
    user: User = request.user

    with transaction.atomic():
        try:
            rotation = Rotation.objects.get(pk=rotation_id)
        except Rotation.DoesNotExist:
            return 404, None

        if rotation.is_closed or not user.has_perm('allianceauth_pve.manage_rotations'):
            return 403, None

        item_ids = set(
            EntryLootItem.objects
            .filter(entry__rotation=rotation)
            .values_list('item_id', flat=True)
            .distinct()
        )

        errors = data.validate(item_ids)
        if errors:
            return 400, errors

        data.save(rotation)

        ensure_rotation_presets_applied()

    summary_cache_key = ROTATION_SUMMARY_CACHE_KEY.format(rotation_id=rotation_id)
    project_summaries_cache_key = ROTATION_PROJECT_SUMMARY_CACHE_KEY.format(rotation_id=rotation_id)

    cache.delete(summary_cache_key)
    cache.delete(project_summaries_cache_key)

    cache.delete_many(
        FUNDING_PROJECT_SUMMARY_CACHE_KEY.format(project_id=pk)
        for pk in FundingProject.objects.affected_by(rotation)
        .values_list('pk', flat=True).distinct()
    )

    cache.delete_many(
        ACTIVITY_CACHE_KEY.format(user_id=user_id, months=months)
        for user_id in EntryCharacter.objects
        .filter(entry__rotation=rotation)
        .values_list('user_id', flat=True).distinct()
        for months in [1, 3, 6, 12]
    )

    return 200, None


@router.get("/{int:rotation_id}/summary/", response={200: list[RotationSummarySchema], 404: None})
def get_rotation_summary(request, rotation_id: int):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, None

    cache_key = ROTATION_SUMMARY_CACHE_KEY.format(rotation_id=rotation_id)
    cached_summary = cache.get(cache_key)
    if cached_summary is not None:
        return 200, cached_summary

    summary = rotation.summary.order_by('-estimated_total').values(
        'helped_setups',
        'estimated_total',
        'actual_total',
        'actual_total_from_items',
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
    cache.set(cache_key, summary, ROTATION_SUMMARY_CACHE_TIMEOUT)

    return 200, summary


@router.get("/{int:rotation_id}/project_summaries/", response={200: list[RotationProjectSummarySchema], 404: None})
def get_rotation_project_summaries(request, rotation_id: int):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, None

    cache_key = ROTATION_PROJECT_SUMMARY_CACHE_KEY.format(rotation_id=rotation_id)
    cached_summaries = cache.get(cache_key)
    if cached_summaries is not None:
        return 200, cached_summaries

    summaries = [
        {'project': project, 'summary': summary}
        for project, summary in rotation.funding_projects_summary.items()
    ]
    cache.set(cache_key, summaries, ROTATION_PROJECT_SUMMARY_CACHE_TIMEOUT)

    return 200, summaries


@router.get("/{int:rotation_id}/role_setups/", response={200: list[RoleSetupSchema], 404: None})
def get_rotation_role_setups(request, rotation_id: int):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, None

    return 200, rotation.roles_setups.prefetch_related('roles')


@router.get("/{int:rotation_id}/buttons/", response={200: list[PveButtonSchema], 404: None})
def get_rotation_buttons(request, rotation_id: int):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, None

    return 200, rotation.entry_buttons.all()


@router.get("/{int:rotation_id}/items/", response={200: list[ExtendedEntryItemSchema], 404: None})
def get_rotation_items(request, rotation_id: int):
    try:
        rotation = Rotation.objects.get(pk=rotation_id)
    except Rotation.DoesNotExist:
        return 404, None

    item_qs = (
        EntryLootItem.objects
        .filter(entry__rotation=rotation)
        .with_total_after_tax()
        .values('item_id', 'item__name')
        .annotate(quantity=Sum('quantity'))
        .annotate(sale_price=Sum('sale_price'))
        .annotate(total_after_tax=Sum('total_after_tax'))
    )
    return 200, [{
        'id': item['item_id'],
        'name': item['item__name'],
        'quantity': item['quantity'],
        'sale_price': item['sale_price'],
        'total_after_tax': item['total_after_tax'],
    } for item in item_qs]
