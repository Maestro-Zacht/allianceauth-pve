from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone
from ninja import Router

from allianceauth_pve.app_settings import ACTIVITY_CACHE_KEY, ACTIVITY_CACHE_TIMEOUT
from allianceauth_pve.utils import running_averages

from .schema import ActivitySchema

router = Router(tags=["activity"])


@router.get("/months/{int:months}/", response={200: ActivitySchema, 400: str})
def get_activity(request, months: int):
    if months < 1:
        return 400, "Invalid number of months"

    cache_key = ACTIVITY_CACHE_KEY.format(user_id=request.auth.pk, months=months)
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return 200, cached_data

    start_date = timezone.now() - timedelta(days=30 * months)
    result = running_averages(request.auth, start_date)
    cache.set(cache_key, result, ACTIVITY_CACHE_TIMEOUT)

    return 200, result
