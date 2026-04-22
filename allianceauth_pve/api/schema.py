from collections import defaultdict
from datetime import datetime

from ninja import Schema, ModelSchema

from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Sum

from allianceauth.eveonline.models import EveCharacter
from allianceauth.authentication.models import CharacterOwnership

from eve_sde.models import ItemType

from ..models import Entry, EntryCharacter, PveButton, RoleSetup, FundingProject, Rotation, EntryRole, EntryLootItem
from ..app_settings import PVE_ONLY_MAINS


class PermissionsSchema(Schema):
    main_character_id: int
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
    tax_rate_loot_items: float
    actual_total_from_items: float


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
    character_id: int
    main_character_id: int | None
    character_name: str
    estimated_total: float
    actual_total: float
    actual_total_from_items: float

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
    created_by_character: EveCharacterSchema | None
    total_user_count: int
    estimated_total: int
    estimated_total_after_tax: float
    actual_total_after_tax: float
    actual_total_from_items: float

    @staticmethod
    def resolve_created_by_character(obj: Entry) -> EveCharacter | None:
        return obj.created_by.profile.main_character


class BaseRoleSchema(Schema):
    name: str
    value: int


class EntryRoleSchema(BaseRoleSchema):
    role_approximate_percentage: float


class EntryCharacterSchema(Schema):
    user_main_character: EveCharacterSchema | None
    user_character: EveCharacterSchema
    role_name: str
    site_count: int
    helped_setup: bool
    estimated_share_total: float
    estimated_funding_amount: float
    actual_share_total: float
    actual_funding_amount: float
    actual_share_total_for_items: float
    actual_funding_amount_for_items: float

    @staticmethod
    def resolve_user_main_character(obj: EntryCharacter) -> EveCharacter | None:
        return obj.user.profile.main_character

    @staticmethod
    def resolve_role_name(obj: EntryCharacter) -> str:
        return obj.role.name


class EntryDetailsSchema(EntrySchema):
    funding_project: FundingProjectBasicSchema | None
    funding_percentage: int | None

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
    tax_rate_loot_items: float
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

        if self.tax_rate_loot_items < 0.0 or self.tax_rate_loot_items > 100.0:
            errors['tax_rate_loot_items'].append(_('Tax rate must be between 0 and 100.'))

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


class RoleSetupSchema(BaseRoleSetupSchema):
    roles: list[BaseRoleSchema]


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


class ItemSaleValueErrorsSchema(Schema):
    item_id: list[str] = []
    sale_value: list[str] = []


class ItemSaleValueSchema(Schema):
    item_id: int
    sale_value: int

    def validate(self, item_ids: set[int]) -> ItemSaleValueErrorsSchema | None:
        errors = defaultdict(list)

        if not ItemType.objects.filter(pk=self.item_id, published=True).exists():
            errors['item_id'].append(_('Item does not exist or is not published.'))

        if self.sale_value < 0:
            errors['sale_value'].append(_('Sale value must be a non-negative integer.'))

        if self.item_id not in item_ids:
            errors['item_id'].append(_('Item has not been added in this rotation.'))
        else:
            item_ids.remove(self.item_id)

        return ItemSaleValueErrorsSchema(**dict(errors)) if errors else None


class CloseRotationErrorsSchema(Schema):
    sales_value: list[str] = []
    item_sales: dict[int, ItemSaleValueErrorsSchema] = {}
    items_missing: list[int] = []


class CloseRotationSchema(Schema):
    sales_value: int
    item_sales: list[ItemSaleValueSchema]

    def validate(self, item_ids: set[int]) -> CloseRotationErrorsSchema | None:
        errors = defaultdict(list)

        if self.sales_value < 0:
            errors['sales_value'].append(_('Sales value must be a non-negative integer.'))

        item_sales_errors = {}
        for i, item_sale in enumerate(self.item_sales):
            item_sale_errors = item_sale.validate(item_ids)
            if item_sale_errors is not None:
                item_sales_errors[i] = item_sale_errors
        if item_sales_errors:
            errors['item_sales'] = item_sales_errors

        if len(item_ids) > 0:
            errors['items_missing'] = list(item_ids)

        return CloseRotationErrorsSchema(**dict(errors)) if errors else None

    def save(self, rotation: Rotation):
        rotation.actual_total = self.sales_value
        rotation.is_closed = True
        rotation.closed_at = timezone.now()
        rotation.save(update_fields=['actual_total', 'is_closed', 'closed_at'])

        for item_sale in self.item_sales:
            total_quantity = EntryLootItem.objects.filter(
                entry__rotation=rotation,
                item_id=item_sale.item_id
            ).aggregate(total=Sum('quantity'))['total']

            EntryLootItem.objects.filter(
                entry__rotation=rotation,
                item_id=item_sale.item_id
            ).update(sale_price=item_sale.sale_value / total_quantity)


class RoleFormErrorsSchema(Schema):
    name: list[str] = []
    value: list[str] = []


class RoleFormSchema(BaseRoleSchema):

    def validate(self, names: dict[str, int]) -> RoleFormErrorsSchema | None:
        errors = defaultdict(list)

        if len(self.name) == 0 or len(self.name) > 64:
            errors['name'].append(_('Name must be between 1 and 64 characters long.'))
        elif self.name in names:
            errors['name'].append(_('Role names must be unique within the entry.'))
        else:
            names[self.name] = self.value

        if self.value < 0:
            errors['value'].append(_('Value must be non-negative.'))

        if errors:
            return RoleFormErrorsSchema(**dict(errors))
        return None


class ShareFormErrorsSchema(Schema):
    character_id: list[str] = []
    helped_setup: list[str] = []
    site_count: list[str] = []
    role_name: list[str] = []


class ShareFormSchema(Schema):
    character_id: int
    helped_setup: bool
    site_count: int
    role_name: str

    @staticmethod
    def resolve_role_name(obj: EntryCharacter) -> str:
        if type(obj) is EntryCharacter:
            return obj.role.name
        return obj['role_name']

    @staticmethod
    def resolve_character_id(obj: EntryCharacter) -> int:
        if type(obj) is EntryCharacter:
            return obj.user_character.character_id
        return obj['character_id']

    def validate(self, character_ids: set[int], roles: dict[str, int], users: set[int]) -> ShareFormErrorsSchema | None:
        errors = defaultdict(list)

        if self.site_count < 0:
            errors['site_count'].append(_('Site count must be non-negative.'))

        if not EveCharacter.objects.filter(character_id=self.character_id).exists():
            errors['character_id'].append(_('Character does not exist.'))
        elif self.character_id in character_ids:
            errors['character_id'].append(_('Character can only have one share in the entry.'))
        else:
            try:
                user: User = CharacterOwnership.objects.get(character__character_id=self.character_id).user
            except CharacterOwnership.DoesNotExist:
                errors['character_id'].append(_('Character is not owned by any user.'))
            else:
                character_ids.add(self.character_id)
                if PVE_ONLY_MAINS and user.pk in users:
                    errors['character_id'].append(_('A user can only have one share in the entry.'))
                else:
                    users.add(user.pk)

        if self.role_name not in roles:
            errors['role_name'].append(_('Role name must match one of the roles defined in the entry.'))

        if errors:
            return ShareFormErrorsSchema(**dict(errors))
        return None


class EntryItemErrorsSchema(Schema):
    item: list[str] = []
    quantity: list[str] = []


class EntryItemSchema(Schema):
    id: int
    quantity: int

    def validate(self) -> EntryItemErrorsSchema | None:
        errors = defaultdict(list)

        if not ItemType.objects.filter(pk=self.id, published=True).exists():
            errors['item'].append(_('Item does not exist or is not published.'))

        if self.quantity < 1:
            errors['quantity'].append(_('Quantity must be at least 1.'))

        if errors:
            return EntryItemErrorsSchema(**dict(errors))
        return None


class EntryFormErrorsSchema(Schema):
    estimated_total: list[str] = []
    funding_project_id: list[str] = []
    funding_percentage: list[str] = []
    roles_root: list[str] = []
    roles: dict[int, RoleFormErrorsSchema] = {}
    shares_root: list[str] = []
    shares: dict[int, ShareFormErrorsSchema] = {}
    items: dict[int, EntryItemErrorsSchema] = {}


class EntryFormSchema(Schema):
    estimated_total: int
    funding_project_id: int | None
    funding_percentage: int | None

    roles: list[RoleFormSchema]
    shares: list[ShareFormSchema]
    items: list[EntryItemSchema]

    def validate(self) -> EntryFormErrorsSchema | None:
        errors = defaultdict(list)
        roles = {}

        if not self.roles:
            errors['roles_root'].append(_('At least one role is required.'))
        else:
            roles_errors = {}

            for i, role in enumerate(self.roles):
                role_errors = role.validate(roles)
                if role_errors is not None:
                    roles_errors[i] = role_errors
            if roles_errors:
                errors['roles'] = roles_errors

        if not self.shares:
            errors['shares_root'].append(_('At least one share is required.'))
        else:
            shares_errors = {}
            character_ids = set()
            users = set()
            total_value = 0
            for i, share in enumerate(self.shares):
                share_errors = share.validate(character_ids, roles, users)
                if share_errors is not None:
                    shares_errors[i] = share_errors
                total_value += share.site_count * roles.get(share.role_name, 0)

            if shares_errors:
                errors['shares'] = shares_errors
            elif total_value == 0:
                errors['shares_root'].append(_('Form not valid, you need at least 1 person to receive loot'))

        items_errors = {}
        for i, item in enumerate(self.items):
            item_errors = item.validate()
            if item_errors is not None:
                items_errors[i] = item_errors
        if items_errors:
            errors['items'] = items_errors

        if self.estimated_total < 0:
            errors['estimated_total'].append(_('Estimated total must be non-negative.'))
        elif self.estimated_total == 0 and len(self.items) == 0:
            errors['estimated_total'].append(_('Estimated total must be at least 1 ISK or you must add at least one item.'))

        if self.funding_project_id is not None and not FundingProject.objects.filter(pk=self.funding_project_id, is_active=True).exists():
            errors['funding_project_id'].append(_('Funding project does not exist or is not active.'))
        elif self.funding_project_id is not None and self.funding_percentage is None:
            errors['funding_percentage'].append(_('Funding percentage is required when a funding project is specified.'))
        elif self.funding_percentage is not None and (self.funding_percentage < 1 or self.funding_percentage > 100):
            errors['funding_percentage'].append(_('Funding percentage must be between 1 and 100.'))

        if errors:
            return EntryFormErrorsSchema(**dict(errors))
        return None

    def save(self, created_by: User, rotation: Rotation, entry: Entry | None = None) -> Entry:
        if entry is None:
            entry = Entry.objects.create(
                rotation=rotation,
                created_by=created_by,
                estimated_total=self.estimated_total,
                funding_project_id=self.funding_project_id,
                funding_percentage=self.funding_percentage,
            )
        else:
            entry.loot_items.all().delete()
            entry.ratting_shares.all().delete()
            entry.roles.all().delete()
            entry.estimated_total = self.estimated_total
            entry.funding_project_id = self.funding_project_id
            entry.funding_percentage = self.funding_percentage
            entry.save()

        roles_to_add = [EntryRole(entry=entry, name=role.name, value=role.value) for role in self.roles]
        EntryRole.objects.bulk_create(roles_to_add)

        shares_to_add = []
        setups = set()

        for share in self.shares:
            role: EntryRole = entry.roles.get(name=share.role_name)
            ownership: CharacterOwnership = CharacterOwnership.objects.get(character__character_id=share.character_id)

            setup = share.helped_setup and ownership.user_id not in setups
            if setup:
                setups.add(ownership.user_id)

            shares_to_add.append(
                EntryCharacter(
                    entry=entry,
                    role=role,
                    user_character_id=ownership.character_id,
                    user_id=ownership.user_id,
                    site_count=share.site_count,
                    helped_setup=setup
                )
            )

        items_to_add = [EntryLootItem(entry=entry, item_id=item.id, quantity=item.quantity) for item in self.items]
        EntryLootItem.objects.bulk_create(items_to_add)
        EntryCharacter.objects.bulk_create(shares_to_add)

        return entry


class ItemSchema(ModelSchema):
    id: int
    icon_url: str

    class Meta:
        model = ItemType
        fields = ['id', 'name']

    @staticmethod
    def resolve_icon_url(obj: ItemType) -> str:
        if type(obj) is ItemType:
            obj_id = obj.id
        else:
            obj_id = obj['id']
        return f"https://images.evetech.net/types/{obj_id}/icon"


class ItemSearchResultSchema(ItemSchema):
    quantity: int


class ExtendedEntryItemSchema(ItemSearchResultSchema):
    sale_price: float | None
    total_after_tax: float | None


class ExtendedShareFormSchema(ShareFormSchema):
    portrait_url: str
    character_name: str
    main_character_name: str
    main_character_portrait_url: str

    @staticmethod
    def resolve_portrait_url(obj: EntryCharacter) -> str:
        return obj.user_character.portrait_url_32.split('?')[0]

    @staticmethod
    def resolve_character_name(obj: EntryCharacter) -> str:
        return obj.user_character.character_name

    @staticmethod
    def resolve_main_character_name(obj: EntryCharacter) -> str:
        return obj.user.profile.main_character.character_name

    @staticmethod
    def resolve_main_character_portrait_url(obj: EntryCharacter) -> str:
        return obj.user.profile.main_character.portrait_url_32.split('?')[0]


class ExtendedEntryFormSchema(EntryFormSchema):
    shares: list[ExtendedShareFormSchema]
    items: list[ItemSearchResultSchema]

    @staticmethod
    def resolve_items(obj: Entry) -> list[ItemSearchResultSchema]:
        items = EntryLootItem.objects.filter(entry=obj).select_related('item')
        return [{'id': item.item_id, 'quantity': item.quantity, 'name': item.item.name} for item in items]


class RatterSchema(Schema):
    character: EveCharacterSchema
    main_character: EveCharacterSchema
    extra_chars: list[str]

    @staticmethod
    def resolve_main_character(obj: CharacterOwnership) -> EveCharacter:
        return obj.user.profile.main_character

    @staticmethod
    def resolve_extra_chars(obj: CharacterOwnership) -> list[str]:
        if obj.character != obj.user.profile.main_character:
            return []
        return list(map(lambda alt: alt.character.character_name, obj.user.alts))
