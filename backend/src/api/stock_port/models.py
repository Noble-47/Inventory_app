from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CancelOrder(BaseModel):
    order_id: UUID
    reason: str | None = Field(default=None)


class OrderLine(BaseModel):
    name: str
    expected_quantity: int
    cost: float


class Order(BaseModel):
    shop_id: UUID
    supplier: str
    supplier_phone: str
    orderline: list[OrderLine]
    expected_delivery_date: datetime


class OrderSlim(BaseModel):
    order_id: UUID
    supplier: str
    supplies_phone: str
    status: str
    expected_delivery_date: datetime


class ShopOrders(BaseModel):
    shop_id: UUID
    orders: list[OrderSlim]


class SupplierSlim(BaseModel):
    name: str
    phone_number: str


class Supplier(SupplierSlim):
    supplies: list[OrderSlim]


class ShopSuppliers(BaseModel):
    shop_id: str
    suppliers: list[SupplierSlim]
