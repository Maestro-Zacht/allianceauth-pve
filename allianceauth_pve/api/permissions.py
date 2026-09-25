from django.contrib.auth.models import User
from ninja import Router

from allianceauth_pve.app_settings import PVE_ONLY_MAINS

from .schema import PermissionsSchema

router = Router(tags=["permissions"])


@router.get("/", response=PermissionsSchema)
def list_permissions(request):
    user: User = User.objects.select_related("profile__main_character").get(
        pk=request.user.pk
    )
    return {
        "main_character_id": user.profile.main_character.character_id,
        "access_pve": user.has_perm("allianceauth_pve.access_pve"),
        "manage_entries": user.has_perm("allianceauth_pve.manage_entries"),
        "manage_rotations": user.has_perm("allianceauth_pve.manage_rotations"),
        "manage_funding_projects": user.has_perm(
            "allianceauth_pve.manage_funding_projects"
        ),
        "is_superuser": user.is_superuser,
        "pve_only_mains": PVE_ONLY_MAINS,
    }
