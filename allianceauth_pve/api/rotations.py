from ninja import Router

from django.db.models import Count

from ..models import Rotation

from .schema import RotationSchema

router = Router(tags=["rotations"])


@router.get("/rotations", response=list[RotationSchema])
def list_rotations(request):
    return Rotation.objects.annotate(
        number_of_members=Count(
            'entries__ratting_shares__user',
            distinct=True
        )
    )
