from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Unit(BaseModel):
    product: str
    units: int
    price: float


class Sale(BaseModel):
    ref: str | None = Field(default=None)
    customer_name: str
    customer_phone: str
    units: list[Unit]
    date: datetime
    sale_price: float
    amount_paid: float
    payment_completed: bool


class SaleModel(Sale):
    shop_id: UUID


class SaleList(BaseModel):
    shop_id: UUID
    sales: list[Sale]


# Query Models
class SaleQueryParams(BaseModel):
    ref: str | None = Field(default=None)
    customer_name: str | None = Field(defualt=None)
    customer_phone: str | None = Field(defualt=None)
    product: str | None = Field(defualt=None)

    start_date: datetime | None = Field(defualt=None)
    end_date: datetime | None = Field(defualt=None)
