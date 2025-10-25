from datetime import datetime

from pydantic import BaseModel, Field


class Debt(BaseModel):
    value: float
    count: int
    delta: float


class Order(BaseModel):
    value: float
    count: int
    delta: float


class Sale(BaseModel):
    value: float
    count: int
    delta: float


class Inventory(BaseModel):
    value: float
    count: int
    delta: float


class AnalyticReport(BaseModel):
    order: Order
    sale: Sale
    inventory: Inventory
    debt: Debt
    profit: float
    profit_delta: float
    last_updated: datetime | None = Field(default=None)
