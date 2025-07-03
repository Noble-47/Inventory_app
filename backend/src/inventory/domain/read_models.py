import uuid

from pydantic import BaseModel, Field
from datetime import datetime


class Stocks(BaseModel):
    id : int | None = Field(default=None)
    sku:str
    name:str
    level:int
    last_sale:datetime


class Batches(BaseModel):
    id : int | None = Field(default=None)
    sku:str
    ref:str
    price:float
    quantity:int = Field(serialization_alias="available")
    stock_time:datetime
    stock_in_units:int


class InventoryView(BaseModel):
    id : int | None = Field(default=None)
    shop_id:uuid.UUID
    stocks: list[Stocks]
    cogs: float
    value: float


class StockView(BaseModel):
    id : int | None = Field(default=None)
    shop_id:uuid.UUID
    sku:str
    level:int
    last_sale:datetime
    batches: list[Batches]
    cogs: float
    value: float
