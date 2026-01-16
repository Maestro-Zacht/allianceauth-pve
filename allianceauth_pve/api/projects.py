from ninja import Router

from django.db.models import Count, OuterRef, Subquery

from .schema import FundingProjectSchema
from ..models import FundingProject, EntryCharacter

router = Router(tags=["projects"])


@router.get("/", response=list[FundingProjectSchema])
def list_projects(request):
    shares_qs = (
        EntryCharacter.objects.filter(
            entry__funding_project__pk=OuterRef('pk'),
            entry__funding_percentage__gt=0
        )
        .values('entry__funding_project')
        .annotate(num_users=Count('user', distinct=True))
        .values('num_users')
    )

    return FundingProject.objects.annotate(
        number_of_participants=Subquery(shares_qs)
    )
