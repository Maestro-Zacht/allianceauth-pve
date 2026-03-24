from ninja import Router

from django.db.models import Count, OuterRef, Subquery, F
from django.db.models.functions import Coalesce
from django.utils.translation import gettext as _
from django.utils import timezone

from .schema import FundingProjectSchema, SummarySchema, NewProjectSchema
from ..models import FundingProject, EntryCharacter
from .authenticators import NeedsPermission

router = Router(tags=["projects"])


@router.get("/", response=list[FundingProjectSchema])
def list_projects(request):
    shares_qs = (
        EntryCharacter.objects.filter(
            entry__funding_project_id=OuterRef('pk'),
            entry__funding_percentage__gt=0
        )
        .values('entry__funding_project')
        .annotate(num_users=Count('user', distinct=True))
        .values('num_users')
    )

    return FundingProject.objects.annotate(
        number_of_participants=Coalesce(Subquery(shares_qs), 0)
    )


@router.post("/", response={200: int, 400: dict[str, list[str]]}, auth=NeedsPermission('allianceauth_pve.manage_funding_projects'))
def create_project(request, data: NewProjectSchema):
    errors = data.validate()
    if errors:
        return 400, errors

    project = FundingProject.objects.create(**data.dict())
    return 200, project.pk


@router.get("/{int:project_id}/", response={200: FundingProjectSchema, 404: None})
def get_project(request, project_id: int):
    shares_qs = (
        EntryCharacter.objects.filter(
            entry__funding_project_id=OuterRef('pk'),
            entry__funding_percentage__gt=0
        )
        .values('entry__funding_project')
        .annotate(num_users=Count('user', distinct=True))
        .values('num_users')
    )

    try:
        return 200, FundingProject.objects.annotate(
            number_of_participants=Coalesce(Subquery(shares_qs), 0)
        ).get(pk=project_id)
    except FundingProject.DoesNotExist:
        return 404, None


@router.get("/{int:project_id}/summary/", response={200: list[SummarySchema], 404: None})
def get_project_summary(request, project_id: int):
    try:
        project = FundingProject.objects.get(pk=project_id)
    except FundingProject.DoesNotExist:
        return 404, None

    return 200, project.summary.order_by('-estimated_total').values(
        'actual_total',
        'estimated_total',
        character_name=F('user__profile__main_character__character_name'),
        character_id=F('user__profile__main_character__character_id'),
    )


@router.post(
    "/{int:project_id}/complete/",
    response={200: None, 400: str, 403: str, 404: None},
    auth=NeedsPermission('allianceauth_pve.manage_funding_projects')
)
def toggle_complete_project(request, project_id: int):
    try:
        funding_project = FundingProject.objects.get(pk=project_id)
    except FundingProject.DoesNotExist:
        return 404, None

    if funding_project.is_active and funding_project.has_open_contributions:
        return 403, _("You cannot complete a project with open contributions")

    if not funding_project.is_active and FundingProject.objects.filter(is_active=True, name=funding_project.name).exists():
        return 400, _("You cannot reopen this project, another one with the same name is active.")

    funding_project.is_active = not funding_project.is_active
    if funding_project.is_active:
        funding_project.completed_at = None
    else:
        funding_project.completed_at = timezone.now()

    funding_project.save()

    return 200, None
