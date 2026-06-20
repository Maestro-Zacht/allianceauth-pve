from typing import TYPE_CHECKING

from ninja import Router

from .schema import PermissionsSchema

if TYPE_CHECKING:
    from django.contrib.auth.models import User

router = Router(tags=["permissions"])


@router.get("/", response=PermissionsSchema)
def list_permissions(request):
    user: User = request.user
    return {
        "main_character_id": user.profile.main_character.character_id,
        "access_pve": user.has_perm("allianceauth_pve.access_pve"),
        "manage_entries": user.has_perm("allianceauth_pve.manage_entries"),
        "manage_rotations": user.has_perm("allianceauth_pve.manage_rotations"),
        "manage_funding_projects": user.has_perm(
            "allianceauth_pve.manage_funding_projects"
        ),
        "is_superuser": user.is_superuser,
    }
