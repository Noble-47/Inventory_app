from typing import Literal, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class OrderedProducts(BaseModel):
    sku: str
    quantity: int
    cost: float


class Delivery(BaseModel):
    orderline: dict[str, int]


class Command(BaseModel):
    pass


class CreateShopRecord(Command):
    shop_id: UUID


class DeleteShopRecord(Command):
    shop_id: UUID


class CreateOrder(Command):
    shop_id: UUID
    orderline: list[OrderedProducts]
    delivery_date: datetime
    firstname: str
    lastname: str
    phone: str


class DeleteOrder(Command):
    shop_id: UUID
    order_id: UUID


class CancelOrder(Command):
    shop_id: UUID
    order_id: UUID
    reason: str


class ProcessDelivery(BaseModel):
    shop_id: UUID
    order_id: UUID
    orderline: dict[str, dict[str, Any]]
