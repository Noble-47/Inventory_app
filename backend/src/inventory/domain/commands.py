from dataclasses import dataclass
from datetime import datetime
import uuid

class Command:
    pass

class CreateStock(Command):
    """Allow user to add stock directly during app setup period."""
    shop_id:uuid.UUID
    name:str
    time:datetime
    price:float
    quantity:int

@dataclass
class AddBatchToStock(Command):
    sku:str
    batch_ref:str
    quantity:int
    price:float
    timestamp:float


@dataclass
class DispatchGoodsFromStock(Command):
    sku:str
    quantity:int
    timestamp:float


@dataclass
class UpdateBatchPrice(Command):
    sku:str
    batch_ref:str
    price:float


@dataclass
class UpdateBatchQuantity(Command):
    sku:str
    batch_ref:str
    quantity:int
