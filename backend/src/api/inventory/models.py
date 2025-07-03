from datetime import datetime
import uuid

from pydantic import BaseModel, Field

# Write Models
class CreateStock(BaseModel):
    """Add a new stock to shop."""
    shop_id:uuid.UUID
    quantity:int = Field(default=0)
    price:float
    time:datetime

# Response Models
class Stock(BaseModel):
    """List of batches of a stock."""
    sku:str
    name:str
    level:int
    last_sale:datetime

class ShopView(BaseModel):
    "View all the stocks in a shop."""
    shop_id:uuid.UUID
    stocks: list[Stock]
    cogs:float
    value:float

class Batch(BaseModel):
    ref:str
    price:float
    available:int
    stock_time: datetime
    stock_in_units: int

class StockView(Stock):
    shop_id:uuid.UUID
    sku:str
    batches : list[Batch]
    cogs : float
    value : float


class Log(BaseModel):
    time:datetime
    description:str
    payload:dict

class BatchLog(Log):
    batch_ref: str

class StockLog(Log):
    sku:str

class StockAudit(BaseModel):
    """View every action taken on stock (e.g dispatch, update, batch_add, etc)."""
    audit_id:int
    shop_id:uuid.UUID
    sku:str
    batch_logs:list[BatchLog]

class ShopAudit(BaseModel):
    """View every action taken on all stocks in a shop."""
    audit_id:int
    shop_id:uuid.UUID
    stock_logs : list[StockLog]
