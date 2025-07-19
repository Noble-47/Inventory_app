from datetime import datetime
import uuid

from pydantic import BaseModel, Field


# Write Models
class CreateStock(BaseModel):
    """Add a new stock to shop."""

    name: str
    quantity: int = Field(default=0)
    price: float


# Response Models
class Stock(BaseModel):
    """List of batches of a stock."""

    sku: str
    name: str
    level: int
    last_sale: datetime | None = Field(default=None)


class ShopView(BaseModel):
    "View all the stocks in a shop." ""
    shop_id: uuid.UUID
    stocks: list[Stock]
    cogs: float
    value: float


class Batch(BaseModel):
    ref: str
    price: float
    available: int = Field(validation_alias="quantity")
    stock_time: datetime
    stock_in_units: int


class StockView(Stock):
    shop_id: uuid.UUID
    sku: str
    batches: list[Batch]
    cogs: float
    value: float


class Log(BaseModel):
    audit_id: int
    time: datetime
    description: str
    payload: dict


class StockAudit(BaseModel):
    """View every action taken on stock (e.g dispatch, update, batch_add, etc)."""

    shop_id: uuid.UUID
    sku: str
    logs: list[Log]


class BatchAudit(BaseModel):
    """View every action taken on all batches of a stock in a shop."""

    shop_id: str
    sku: str
    ref: str
    quantity: int = Field(serialization_alias="available")
    stock_time: datetime = Field(serialization_alias="stock_date")
    price: float
    stock_in_units: int = Field(serialization_alias="stock_units")
    logs: list[Log]
