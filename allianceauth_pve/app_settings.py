from django.conf import settings

PVE_ONLY_MAINS = getattr(settings, 'PVE_ONLY_MAINS', False)
