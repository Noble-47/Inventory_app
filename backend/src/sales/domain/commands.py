from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Command(BaseModel):
    pass


class CreateShopRecord(Command):
    shop_id: UUID


class DeleteShopRecord(Command):
    shop_id: UUID


class Record(BaseModel):
    name: str
    cogs: float
    value: int
    price: float


class CreateSale(Command):
    shop_id: UUID
    phone_number: str
    firstname: str
    lastname: str
    products: list[dict[str, Any]]
    selling_price: float
    amount_paid: float
    inventory_record: dict[str, Record]


class UpdateSale(Command):
    shop_id: UUID
    ref: UUID
    updates: dict[str, Any]


class DeleteSale(Command):
    shop_id: UUID
    ref: UUID
