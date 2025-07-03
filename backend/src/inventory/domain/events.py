from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import uuid
import pytz

from inventory import config

timezone = config.TIMEZONE

class Event:

    def __post_init__(self):
        self.name = self.__class__.__name__
        self.time = datetime.now(timezone)

    @property
    def event_hash(self):
        attrs = list(str(v) for k,v in asdict(self) if k not in ['time', 'description'])
        raw = "|".join(attrs).encode()
        return hashlib.sha256(raw).hexdigest()

    @property
    def payload(self):
        return asdict(self)

    def serialize(self):
        return {
            "name" : self.name,
            "sku": self.sku,
            "description" : self.description,
            "payload" : self.payload,
            "event_hash" : self.event_hash,
            "time" : self.time
        }


@dataclass
class BatchAddedToStock(Event):
    shop_id:uuid.UUID
    sku: str
    batch_ref: str
    quantity: float
    price: float
    stock_time: datetime

    @property
    def description(self):
        return f"Added {self.quantity} units to {self.sku}"


@dataclass
class DispatchedFromStock(Event):
    shop_id:uuid.UUID
    sku: str
    quantity: float
    dispatch_time: datetime

    @property
    def description(self):
        return f"Dispatched {self.quantity} units from {self.sku}"


@dataclass
class DispatchedFromBatch(Event):
    sku:str
    batch_ref:str
    quantity:int


@dataclass
class StockSoldOut(Event):
    shop_id:uuid.UUID
    sku: str
    when: datetime

    @property
    def description(self):
        return f"Sold out {self.sku}"

@dataclass
class BatchSoldOut(Event):
    sku: str
    batch_ref: str
    when: datetime

    @property
    def description(self):
        return f"Sold out {self.sku}"


@dataclass
class UpdatedBatchPrice(Event):
    sku: str
    batch_ref: str
    price: str

    @property
    def description(self):
        return f"Updated {self.sku} price to {self.price}"


@dataclass
class AdjustedStockLevel(Event):
    shop_id:uuid.UUID
    sku: str
    on: str # actual batch updated
    by: int
    batch_adjustment_record:list[dict[str, int]]

    @property
    def description(self):
        return f"Updated batch-{self.on} by {self.by}"


@dataclass
class IncreasedStockLevel(AdjustedStockLevel):
    pass


@dataclass
class DecreasedStockLevel(AdjustedStockLevel):
    pass
