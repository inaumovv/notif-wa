from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Union, Optional

from pydantic import BaseModel


class Status(Enum):
    INRENT = 'inrent'
    DEBTOR = 'debtor'
    EXCEED = 'exceed'
    SOON_EXCEED = 'soon_exceed'
    COMPLETED = 'completed'


class InventoryItem(BaseModel):
    id: int
    name: str


class Client(BaseModel):
    phone: str
    name: str


class LastExceedNotification(BaseModel):
    every_3_hours: Optional[datetime] = None
    every_day: Optional[datetime] = None


class RentEntity(BaseModel):
    id: int
    status: Status
    client: Client
    rent_start: datetime
    rent_end: datetime
    price: Decimal
    day_price: Decimal
    inventories: Union[list[InventoryItem], InventoryItem]
    time_exceed: bool
    penalty: Optional[Decimal] = None
    last_exceed_notification: LastExceedNotification = LastExceedNotification(
        every_3_hours=None,
        every_day=None
    )


