from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import pytz

from inventory import config

timezone = config.TIMEZONE

class Event:

    def __post_init__(self):
        self.name = self.__class__.__name__
        self.time = datetime.now(timezone)

    @property
    def event_hash(self):
        attrs = list(str(v) for k,v in asdict(self) if k != 'time')
        raw = "|".join(attrs).encode()
        return hashlib.sha256(raw).hexdigest()

    @property
    def payload(self):
        return asdict(self)

    def serialize(self):
        return {
            "name" : self.name,
            "sku": self.sku,
            "version_number" : self.version_number,
            "payload" : self.payload,
            "event_hash" : self.event_hash,
            "time" : self.time
        }


@dataclass
class BatchAddedToStock(Event):
    sku: str
    version_number:int
    batch_ref: str
    quantity: float
    price: float
    stock_time: datetime


@dataclass
class DispatchedFromStock(Event):
    sku: str
    version_number:int
    quantity: float
    dispatch_time: datetime


@dataclass
class StockSoldOut(Event):
    sku: str
    batch_ref: str
    version_number:int
    when: datetime


@dataclass
class UpdatedBatchPrice(Event):
    sku: str
    batch_ref: str
    version_number:int
    price: str


@dataclass
class AdjustedStockLevel(Event):
    sku: str
    version_number:int
    on: str # actual batch updated
    by: int


@dataclass
class IncreasedStockLevel(AdjustedStockLevel):
    pass


@dataclass
class DecreasedStockLevel(AdjustedStockLevel):
    pass
