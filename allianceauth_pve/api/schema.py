from collections import defaultdict
from datetime import datetime
from ninja import Schema, ModelSchema

from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from allianceauth.eveonline.models import EveCharacter

from ..models import Entry, EntryCharacter, PveButton, RoleSetup, FundingProject


class PermissionsSchema(Schema):
    access_pve: bool
    manage_entries: bool
    manage_rotations: bool
    manage_funding_projects: bool
    is_superuser: bool


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


class RotationProjectSummarySchema(Schema):
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


class NewRotationSchema(Schema):
    name: str
    priority: int
    tax_rate: float
    max_daily_setups: int
    min_people_share_setup: int
    entry_buttons: list[int]
    roles_setups: list[int]

    def validate(self) -> dict[str, list[str]]:
        errors = defaultdict(list)

        if len(self.name) == 0 or len(self.name) > 128:
            errors['name'].append(_('Name must be between 1 and 128 characters long.'))

        if self.tax_rate < 0.0 or self.tax_rate > 100.0:
            errors['tax_rate'].append(_('Tax rate must be between 0 and 100.'))

        if self.max_daily_setups < 0:
            errors['max_daily_setups'].append(_('The number of maximum daily setups must be non-negative.'))

        if self.min_people_share_setup < 0:
            errors['min_people_share_setup'].append(_('The minimum number of people required to count a setup valid must be non-negative.'))

        buttons = set(PveButton.objects.values_list('pk', flat=True))
        if any(button_id not in buttons for button_id in self.entry_buttons):
            errors['entry_buttons'].append(_('One or more entry buttons are invalid.'))

        setups = set(RoleSetup.objects.values_list('pk', flat=True))
        if any(role_id not in setups for role_id in self.roles_setups):
            errors['roles_setups'].append(_('One or more roles setups are invalid.'))

        return dict(errors)


class PveButtonSchema(ModelSchema):
    id: int

    class Meta:
        model = PveButton
        fields = ['id', 'text', 'amount']


class BaseRoleSetupSchema(ModelSchema):
    id: int

    class Meta:
        model = RoleSetup
        fields = ['id', 'name']


class NewProjectSchema(Schema):
    name: str
    goal: int

    def validate(self) -> dict[str, list[str]]:
        errors = defaultdict(list)

        if len(self.name) == 0 or len(self.name) > 128:
            errors['name'].append(_('Name must be between 1 and 128 characters long.'))

        if FundingProject.objects.filter(name=self.name, is_active=True).exists():
            errors['name'].append(_('An active project with this name already exists.'))

        if self.goal < 1:
            errors['goal'].append(_('Goal must be at least 1 ISK.'))

        return dict(errors)


class CloseRotationSchema(Schema):
    sales_value: int

    def validate(self) -> dict[str, list[str]]:
        errors = defaultdict(list)

        if self.sales_value < 1:
            errors['sales_value'].append(_('Sales value must be at least 1 ISK.'))

        return dict(errors)
