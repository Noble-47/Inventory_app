from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Unit(BaseModel):
    product_sku: str
    quantity: int


class SaleWrite(BaseModel):
    firstname: str
    lastname: str | None = Field(default=None)
    phone_number: str
    units: list[Unit]
    date: datetime
    selling_price: float
    amount_paid: float


class Sale(SaleWrite):
    ref: str
    payment_completed: bool


class SaleRead(Sale):
    shop_id: UUID


class SaleUpdate:
    firstname: str | None = Field(default=None)
    lastname: str | None = Field(default=None)
    phone: str | None = Field(default=None)
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
    payload: str


class SaleLogs(BaseModel):
    shop_id: UUID
    logs: list[Log] = Field(default_factory=list)


# Query Models
class SaleQueryParams(BaseModel):
    firstname: str | None = Field(default=None)
    lastname: str | None = Field(default=None)
    phone_number: str | None = Field(default=None)
    sku: str | None = Field(default=None)
    product: str | None = Field(default=None)
    start_date: datetime | None = Field(default=None)
    end_date: datetime | None = Field(default=None)
