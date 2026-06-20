from ninja.security import SessionAuth


class CanAccessPVE(SessionAuth):
    def authenticate(self, request, key):
        user = super().authenticate(request, key)
        if user and user.has_perm("allianceauth_pve.access_pve"):
            return user
        return None


class NeedsPermission(CanAccessPVE):
    def __init__(self, permission_codename, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permission_codename = permission_codename

    def authenticate(self, request, key):
        user = super().authenticate(request, key)
        if user and user.has_perm(self.permission_codename):
            return user
        return None
