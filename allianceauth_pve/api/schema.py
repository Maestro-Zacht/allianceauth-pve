from datetime import datetime
from ninja import Schema

from django.contrib.auth.models import User

from allianceauth.eveonline.models import EveCharacter

from ..models import Entry, EntryCharacter


class ActivitySchema(Schema):
    helped_setups: int
    estimated_total: float
    actual_total: float


class RotationSchema(Schema):
    id: int
    name: str
    created_at: datetime
    is_closed: bool
    closed_at: datetime | None = None
    number_of_members: int
    estimated_total: float
    actual_total: float
    priority: int
    tax_rate: float


class FundingProjectBasicSchema(Schema):
    id: int
    name: str


class FundingProjectSchema(FundingProjectBasicSchema):
    goal: int
    is_active: bool
    created_at: datetime
    completed_at: datetime | None = None
    current_total: float
    estimated_total: float
    actual_percentage: float
    estimated_missing_percentage: float
    number_of_participants: int


class SummarySchema(Schema):
    portrait_url: str
    character_name: str
    estimated_total: float
    actual_total: float

    @staticmethod
    def resolve_portrait_url(obj) -> str:
        return (
            EveCharacter
            .generic_portrait_url(obj['character_id'])
            .split('?')[0]
        )


class RotationSummarySchema(SummarySchema):
    helped_setups: int


class ProjectSummarySchema(Schema):
    project: FundingProjectBasicSchema
    summary: list[SummarySchema]


class EveCharacterSchema(Schema):
    character_id: int
    character_name: str
    portrait_url: str

    @staticmethod
    def resolve_portrait_url(obj: EveCharacter) -> str:
        return obj.portrait_url_32.split('?')[0]


class EntrySchema(Schema):
    id: int
    created_at: datetime
    created_by_character: EveCharacterSchema
    total_user_count: int
    total_site_count: int
    estimated_total: int
    estimated_total_after_tax: float
    actual_total_after_tax: float

    @staticmethod
    def resolve_created_by_character(obj: Entry) -> EveCharacter:
        return obj.created_by.profile.main_character


class EntryRoleSchema(Schema):
    name: str
    value: int
    role_approximate_percentage: float


class EntryCharacterSchema(Schema):
    user_main_character: EveCharacterSchema
    user_character: EveCharacterSchema
    role_name: str
    site_count: int
    helped_setup: bool
    estimated_share_total: int
    estimated_funding_amount: int
    actual_share_total: int
    actual_funding_amount: int

    @staticmethod
    def resolve_user_main_character(obj: EntryCharacter) -> EveCharacter:
        return obj.user.profile.main_character

    @staticmethod
    def resolve_role_name(obj: EntryCharacter) -> str:
        return obj.role.name


class EntryDetailsSchema(EntrySchema):
    funding_project: FundingProjectBasicSchema | None
    funding_percentage: int

    rotation_is_closed: bool

    user_can_edit: bool

    @staticmethod
    def resolve_rotation_is_closed(obj: Entry) -> bool:
        return obj.rotation.is_closed

    @staticmethod
    def resolve_user_can_edit(obj: Entry, context) -> bool:
        user: User = context['request'].user
        return user.is_superuser or (
            obj.created_by == user and user.has_perm('allianceauth_pve.manage_entries')
        )
