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
    time: datetime = Field(default_factory=datetime_now_func)
    price: float
    quantity: int


@dataclass
class AddBatchToStock(Command):
    sku: str
    batch_ref: str
    quantity: int
    price: float
    timestamp: float


@dataclass
class DispatchGoodsFromStock(Command):
    sku: str
    quantity: int
    timestamp: float


@dataclass
class UpdateBatchPrice(Command):
    sku: str
    batch_ref: str
    price: float


@dataclass
class UpdateBatchQuantity(Command):
    sku: str
    batch_ref: str
    quantity: int
