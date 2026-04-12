from django.conf import settings

PVE_ONLY_MAINS = getattr(settings, 'PVE_ONLY_MAINS', False)

ACTIVITY_CACHE_KEY = "allianceauth_pve_activity_{user_id}_{months}"
ACTIVITY_CACHE_TIMEOUT = 60 * 60 * 24 * 1  # 1 day

ROTATION_SUMMARY_CACHE_KEY = "allianceauth_pve_rotation_summary_{rotation_id}"
ROTATION_SUMMARY_CACHE_TIMEOUT = 60 * 60 * 24 * 14  # 14 days

ROTATION_PROJECT_SUMMARY_CACHE_KEY = "allianceauth_pve_rotation_project_summaries_{rotation_id}"
ROTATION_PROJECT_SUMMARY_CACHE_TIMEOUT = ROTATION_SUMMARY_CACHE_TIMEOUT

FUNDING_PROJECT_SUMMARY_CACHE_KEY = "allianceauth_pve_funding_project_summary_{project_id}"
FUNDING_PROJECT_SUMMARY_CACHE_TIMEOUT = ROTATION_SUMMARY_CACHE_TIMEOUT
