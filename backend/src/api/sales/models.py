from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Unit(BaseModel):
    product: str
    quantity: int
    price: float


class Sale(BaseModel):
    ref: str | None = Field(default=None)
    customer_name: str
    customer_phone: str
    vunits: list[Unit]
    date: datetime
    selling_price: float
    amount_paid: float
    payment_completed: bool


class SaleModel(Sale):
    shop_id: UUID

class SaleUpdateModel:
    firstname:str | None = Field(default=None)
    lastname:str | None = Field(default=None)
    phone:str | None = Field(default=None)
    selling_price: float | None = Field(default=None)
    amount_paid: float | None = Field(default=None)

class SaleList(BaseModel):
    shop_id: UUID
    sales: list[Sale]

class SaleLog(BaseModel):
    audit_id : int
    shop_id:UUID
    ref:UUID
    description:str
    time:float
    payload:str



# Query Models
class SaleQueryParams(BaseModel):
    ref: str | None = ""
    customer_name: str | None = ""
    customer_phone: str | None = ""
    product: str | None = ""
    start_date: datetime | None = Field(default=None)
    end_date: datetime | None = Field(default=None)
