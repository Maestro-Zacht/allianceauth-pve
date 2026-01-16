from datetime import datetime
from ninja import Schema

from allianceauth.eveonline.models import EveCharacter

from ..models import Entry


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
