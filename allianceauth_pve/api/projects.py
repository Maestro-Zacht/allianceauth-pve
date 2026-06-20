from django.core.cache import cache
from django.db.models import Count, F, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext as _
from ninja import Router

from allianceauth_pve.app_settings import (
    FUNDING_PROJECT_SUMMARY_CACHE_KEY,
    FUNDING_PROJECT_SUMMARY_CACHE_TIMEOUT,
)
from allianceauth_pve.models import EntryCharacter, FundingProject

from .authenticators import NeedsPermission
from .schema import FundingProjectSchema, NewProjectSchema, SummarySchema

router = Router(tags=["projects"])


@router.get("/", response=list[FundingProjectSchema])
def list_projects(request, active: bool | None = None):  # noqa: ARG001
    shares_qs = (
        EntryCharacter.objects.filter(
            entry__funding_project_id=OuterRef("pk"), entry__funding_percentage__gt=0
        )
        .values("entry__funding_project")
        .annotate(num_users=Count("user", distinct=True))
        .values("num_users")
    )

    match active:
        case True:
            base_qs = FundingProject.objects.filter(is_active=True)
        case False:
            base_qs = FundingProject.objects.filter(is_active=False)
        case None:
            base_qs = FundingProject.objects.all()

    return base_qs.annotate(number_of_participants=Coalesce(Subquery(shares_qs), 0))


@router.post(
    "/",
    response={200: int, 400: dict[str, list[str]]},
    auth=NeedsPermission("allianceauth_pve.manage_funding_projects"),
)
def create_project(request, data: NewProjectSchema):  # noqa: ARG001
    errors = data.validate()
    if errors:
        return 400, errors

    project = FundingProject.objects.create(**data.dict())
    return 200, project.pk


@router.get("/{int:project_id}/", response={200: FundingProjectSchema, 404: None})
def get_project(request, project_id: int):  # noqa: ARG001
    shares_qs = (
        EntryCharacter.objects.filter(
            entry__funding_project_id=OuterRef("pk"), entry__funding_percentage__gt=0
        )
        .values("entry__funding_project")
        .annotate(num_users=Count("user", distinct=True))
        .values("num_users")
    )

    try:
        return 200, FundingProject.objects.annotate(
            number_of_participants=Coalesce(Subquery(shares_qs), 0)
        ).get(pk=project_id)
    except FundingProject.DoesNotExist:
        return 404, None


@router.get(
    "/{int:project_id}/summary/", response={200: list[SummarySchema], 404: None}
)
def get_project_summary(request, project_id: int):  # noqa: ARG001
    try:
        project = FundingProject.objects.get(pk=project_id)
    except FundingProject.DoesNotExist:
        return 404, None

    cache_key = FUNDING_PROJECT_SUMMARY_CACHE_KEY.format(project_id=project_id)
    cached_summary = cache.get(cache_key)
    if cached_summary is not None:
        return 200, cached_summary

    summary = project.summary.order_by("-estimated_total").values(
        "actual_total",
        "actual_total_from_items",
        "estimated_total",
        character_name=Coalesce(
            F("user__profile__main_character__character_name"),
            F("user_character__character_name"),
        ),
        character_id=Coalesce(
            F("user__profile__main_character__character_id"),
            F("user_character__character_id"),
        ),
        main_character_id=F("user__profile__main_character__character_id"),
    )
    cache.set(cache_key, summary, FUNDING_PROJECT_SUMMARY_CACHE_TIMEOUT)

    return 200, summary


@router.post(
    "/{int:project_id}/complete/",
    response={200: None, 400: str, 403: str, 404: None},
    auth=NeedsPermission("allianceauth_pve.manage_funding_projects"),
)
def toggle_complete_project(request, project_id: int):  # noqa: ARG001
    try:
        funding_project = FundingProject.objects.get(pk=project_id)
    except FundingProject.DoesNotExist:
        return 404, None

    if funding_project.is_active and funding_project.has_open_contributions:
        return 403, _("You cannot complete a project with open contributions")

    if (
        not funding_project.is_active
        and FundingProject.objects.filter(
            is_active=True, name=funding_project.name
        ).exists()
    ):
        return 400, _(
            "You cannot reopen this project, another one with the same name is active."
        )

    funding_project.is_active = not funding_project.is_active
    if funding_project.is_active:
        funding_project.completed_at = None
    else:
        funding_project.completed_at = timezone.now()

    funding_project.save()

    return 200, None
