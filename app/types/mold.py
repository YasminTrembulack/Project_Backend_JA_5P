from datetime import date, datetime, time

# --- MOLD CLASSES --- #
from typing import List, Literal, Optional
from uuid import UUID

from fastapi import Query
import pytz
from dateutil import parser
from pydantic import BaseModel, field_validator

from app.core.settings import Settings
from app.types.base import BaseQueryParams
from app.types.customer import CustomerResponse
from app.types.enums import (
    ItemStatusEnum,
    PriorityEnum,
)
from app.types.exceptions import InvalidFieldError
from app.types.operation_association import OperationAssociationResponse
from app.types.user import UserResponse

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.types.part import PartResponse


class MoldBase(BaseModel):
    name: Optional[str] = None
    delivery_date: Optional[datetime] = None
    priority: Optional[PriorityEnum] = PriorityEnum.LOW
    progress_percentage: Optional[float] = 0.0
    quantity: Optional[int] = 1
    status: Optional[ItemStatusEnum] = ItemStatusEnum.PENDING
    dimensions: Optional[str] = None
    created_by_id: Optional[str] = None
    created_by: Optional[UserResponse] = None
    customer_id: Optional[str] = None
    customer: Optional[CustomerResponse] = None
    mold_parts: Optional[List['PartResponse']] = []
    operation_associations: Optional[List[OperationAssociationResponse]] = []

    @field_validator('delivery_date', mode='before')
    @classmethod
    def validate_delivery_date(cls, value):
        if value is None:
            return value

        timezone = pytz.timezone(Settings().TZ)
        current_time = datetime.now(timezone)

        if isinstance(value, str):
            try:
                value = parser.parse(value)
            except (ValueError, TypeError):
                raise InvalidFieldError('Invalid date format. Use YYYY-MM-DD.')

        if isinstance(value, date) and not isinstance(value, datetime):
            value_naive = datetime.combine(value, time(23, 59, 59))
            value = timezone.localize(value_naive)

        # Se for datetime sem tzinfo, aplicar o fuso horário
        elif isinstance(value, datetime) and value.tzinfo is None:
            value = timezone.localize(value)

        # Se já tiver fuso, converter para o fuso padrão
        elif isinstance(value, datetime) and value.tzinfo is not None:
            value = value.astimezone(timezone)

        if value < current_time:
            raise InvalidFieldError('Delivery date must be in the future.')

        return value


class MoldPayload(MoldBase):
    delivery_date: datetime
    customer_id: str


class MoldResponse(MoldBase):
    id: UUID
    name: str
    delivery_date: datetime
    priority: PriorityEnum
    quantity: int
    progress_percentage: float
    status: ItemStatusEnum
    dimensions: str | None
    created_by_id: str
    customer_id: str
    created_at: str
    updated_at: str


class MoldUpdatePayload(MoldBase):
    priority: Optional[PriorityEnum] = None
    quantity: Optional[int] = None
    status: Optional[ItemStatusEnum] = None
    progress_percentage: Optional[float] = None


class MoldQueryParams(BaseQueryParams):
    order_by: str = 'created_at'  
