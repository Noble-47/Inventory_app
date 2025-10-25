from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from shared import datetime_now_func


class Unit(BaseModel):
    product_sku: str
    quantity: int


class SaleWrite(BaseModel):
    firstname: str
    lastname: str
    phone_number: str
    units: list[Unit]
    selling_price: float
    amount_paid: float


class Sale(SaleWrite):
    ref: str
    payment_completed: bool


class SaleRead(Sale):
    shop_id: UUID


class SaleUpdate(BaseModel):
    selling_price: float | None = Field(default=None)
    amount_paid: float | None = Field(default=None)


class SaleList(BaseModel):
    shop_id: UUID
    sales: list[Sale]


class Log(BaseModel):
    audit_id: int
    ref: UUID
    description: str
    time: float
    payload: dict[str, Any]


class SaleLogs(BaseModel):
    shop_id: UUID
    logs: list[Log] = Field(default_factory=list)


class CustomerWrite(BaseModel):
    phone: str
    firstname: str
    lastname: str
    new_phone: str | None = Field(default=None)


class Purchase(BaseModel):
    ref: UUID
    selling_price: float
    amount_paid: float
    products: list[Unit]
    date: datetime


class CustomerRead(BaseModel):
    phone: str
    firstname: str
    lastname: str
    purchases: list[Purchase]


class ShopCustomer(BaseModel):
    shop_id: UUID
    customers: list[CustomerRead]
