from dataclasses import dataclass
from datetime import datetime
from typing import Annotated
import uuid

from pydantic import BaseModel, Field, field_validator
from pydantic.functional_serializers import PlainSerializer

from shared import datetime_now_func

StrUUID = Annotated[uuid.UUID, PlainSerializer(lambda x: str(x), return_type=str)]


class Command(BaseModel):

    @field_validator("shop_id", check_fields=False)
    def convert_to_string(cls, shop_id):
        return str(shop_id)


class DeleteStock(Command):
    "Delete stock"
    shop_id: StrUUID
    sku: str


class CreateStock(Command):
    """Allow user to add stock directly during app setup period."""

    shop_id: StrUUID
    name: str
    brand: str
    packet_type: str
    packet_size: str
    time: datetime = Field(default_factory=datetime_now_func)
    price: float
    quantity: int


class AddBatchToStock(Command):
    shop_id: StrUUID
    sku: str
    batch_ref: str
    quantity: int
    price: float
    timestamp: datetime


class DispatchGoods(Command):
    shop_id: StrUUID
    sku: str
    quantity: int
    timestamp: datetime


class UpdateBatchPrice(Command):
    shop_id: StrUUID
    sku: str
    batch_ref: str
    price: float


class UpdateBatchQuantity(Command):
    shop_id: StrUUID
    sku: str
    batch_ref: str
    quantity: int


class UpdateStockQuantity(Command):
    shop_id: StrUUID
    sku: str
    quantity: float
    incremental: bool


class UpdateSetting(Command):
    shop_id: StrUUID
    name: str
    value: str


class CreateInventory(Command):
    shop_id: StrUUID


class DeleteInventory(Command):
    shop_id: StrUUID
