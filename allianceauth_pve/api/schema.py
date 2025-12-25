from datetime import datetime

from ninja import Schema


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


class FundingProjectSchema(Schema):
    id: int
    name: str
    goal: int
    is_active: bool
    created_at: datetime
    completed_at: datetime | None = None
    current_total: float
    estimated_total: float
    actual_percentage: float
    estimated_missing_percentage: float
    number_of_participants: int
