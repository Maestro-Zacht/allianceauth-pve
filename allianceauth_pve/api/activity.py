from datetime import timedelta
from ninja import Router

from django.utils import timezone

from ..utils import running_averages
from .schema import ActivitySchema


router = Router(tags=["activity"])


@router.get("/months/{int:months}/", response={200: ActivitySchema, 400: str})
def get_activity(request, months: int):
    if months < 1:
        return 400, "Invalid number of months"

    start_date = timezone.now() - timedelta(days=30 * months)
    return 200, running_averages(request.auth, start_date)
