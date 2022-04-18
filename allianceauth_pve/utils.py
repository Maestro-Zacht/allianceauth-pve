from django.contrib.auth.models import User
from django.db.models import Q

ratting_users = User.objects.filter(
    Q(groups__permissions__codename='access_pve') |
    Q(user_permissions__codename='access_pve') |
    Q(profile__state__permissions__codename='access_pve'),
    profile__main_character__isnull=False,
).distinct()
