import json

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter
from allianceauth.tests.auth_utils import AuthUtils
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http.response import HttpResponse
from django.test import TestCase
from django.urls import reverse
from eve_sde.models import ItemGroup, ItemType

from allianceauth_pve.models import (
    Entry,
    EntryCharacter,
    EntryLootItem,
    EntryRole,
    Rotation,
)

ACCESS = "allianceauth_pve.access_pve"
MANAGE_ENTRIES = "allianceauth_pve.manage_entries"
MANAGE_ROTATIONS = "allianceauth_pve.manage_rotations"
MANAGE_PROJECTS = "allianceauth_pve.manage_funding_projects"


def url(name, **kwargs):
    return reverse(f"allianceauth_pve:api:{name}", kwargs=kwargs)


class PveApiTestBase(TestCase):
    # ---- user / character helpers -------------------------------------

    @staticmethod
    def make_ownership(user, char: EveCharacter) -> CharacterOwnership:
        return CharacterOwnership.objects.create(
            character=char, user=user, owner_hash=f"oh-{char.character_id}"
        )

    @classmethod
    def make_user(cls, username, char_id, char_name, perms=(), *, ownership=True):
        """Create a user with a main character (and ownership) and permissions."""
        user = AuthUtils.create_user(username)
        char = AuthUtils.add_main_character_2(user, char_name, char_id)
        if ownership:
            cls.make_ownership(user, char)
        if perms:
            user = AuthUtils.add_permissions_to_user_by_name(list(perms), user)
        return user, char

    @classmethod
    def make_superuser(cls, username, char_id, char_name):
        user = AuthUtils.create_user(username)
        user.is_superuser = True
        user.save()
        char = AuthUtils.add_main_character_2(user, char_name, char_id)
        cls.make_ownership(user, char)
        return User.objects.get(pk=user.pk), char

    @classmethod
    def add_alt(cls, user, char_id, char_name):
        char = EveCharacter.objects.create(
            character_id=char_id,
            character_name=char_name,
            corporation_id=2345,
            corporation_name="",
        )
        cls.make_ownership(user, char)
        return char

    # ---- model builders -----------------------------------------------

    @staticmethod
    def make_rotation(name="rot", **kwargs):
        return Rotation.objects.create(name=name, **kwargs)

    @staticmethod
    def make_entry(  # noqa: PLR0913
        rotation,
        user,
        char,
        *,
        role_name="dps",
        role_value=10,
        site_count=1,
        helped_setup=False,
        estimated_total=1_000_000_000,
        funding_project=None,
        funding_percentage=None,
    ):
        entry = Entry.objects.create(
            rotation=rotation,
            created_by=user,
            estimated_total=estimated_total,
            funding_project=funding_project,
            funding_percentage=funding_percentage,
        )
        role = EntryRole.objects.create(entry=entry, name=role_name, value=role_value)
        share = EntryCharacter.objects.create(
            entry=entry,
            user=user,
            user_character=char,
            role=role,
            site_count=site_count,
            helped_setup=helped_setup,
        )
        return entry, role, share

    @staticmethod
    def make_loot_item(entry, item, quantity=1, sale_price=None):
        return EntryLootItem.objects.create(
            entry=entry, item=item, quantity=quantity, sale_price=sale_price
        )

    @staticmethod
    def make_item(item_id, name, *, group_id=None, published=True):
        if group_id is not None and not ItemGroup.objects.filter(pk=group_id).exists():
            ItemGroup.objects.create(id=group_id, name=f"grp{group_id}", published=True)
        return ItemType.objects.create(
            id=item_id, name=name, group_id=group_id, published=published
        )

    # ---- payload builders ---------------------------------------------

    @staticmethod
    def valid_entry_payload(char_id, role_name="dps", **overrides):
        payload = {
            "estimated_total": 1_000_000,
            "funding_project_id": None,
            "funding_percentage": None,
            "roles": [{"name": role_name, "value": 10}],
            "shares": [
                {
                    "character_id": char_id,
                    "helped_setup": False,
                    "site_count": 1,
                    "role_name": role_name,
                }
            ],
            "items": [],
        }
        payload.update(overrides)
        return payload

    @staticmethod
    def rotation_payload(**overrides):
        payload = {
            "name": "New Rotation",
            "priority": 100,
            "tax_rate": 10.0,
            "tax_rate_loot_items": 5.0,
            "max_daily_setups": 1,
            "min_people_share_setup": 3,
            "entry_buttons": [],
            "roles_setups": [],
        }
        payload.update(overrides)
        return payload

    # ---- request helpers ----------------------------------------------

    def api_request(
        self, method, name, body=None, *, query="", **kwargs
    ) -> HttpResponse:
        return self.client.generic(
            method,
            url(name, **kwargs) + query,
            data=json.dumps(body),
            content_type="application/json",
        )

    def setUp(self):
        cache.clear()
