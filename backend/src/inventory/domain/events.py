from dataclasses import dataclass, asdict
from datetime import datetime
from uuid import UUID
import hashlib
import pytz

from inventory import config

timezone = config.TIMEZONE


class Event:

    def __post_init__(self):
        self.name = self.__class__.__name__
        self.event_time = datetime.now(timezone)

    @property
    def event_hash(self):
        model_dump = asdict(self)
        model_dump["time"] = self.event_time
        attrs = list(str(v) for k, v in model_dump.items() if k != "description")
        raw = "|".join(attrs).encode()
        return hashlib.sha256(raw).hexdigest()

    @property
    def payload(self):
        model_dump = asdict(self)
        model_dump.pop("sku")
        model_dump.pop("shop_id")
        for k, v in model_dump.items():
            if isinstance(v, datetime):
                model_dump[k] = v.timestamp()
        return model_dump


class StockEvent(Event):
    def serialize(self):
        return {
            "name": self.name,
            "sku": self.sku,
            "shop_id": self.shop_id,
            "description": self.description,
            "payload": self.payload,
            "event_hash": self.event_hash,
            "event_time": self.event_time,
        }


class BatchEvent(Event):
    def serialize(self):
        return {
            "name": self.name,
            "sku": self.sku,
            "shop_id": self.shop_id,
            "batch_ref": self.batch_ref,
            "description": self.description,
            "payload": self.payload,
            "event_hash": self.event_hash,
            "event_time": self.event_time,
        }


@dataclass
class StockCreated(StockEvent):
    product: str
    sku: str
    shop_id: UUID
    level: float

    @property
    def description(self):
        return f"Added new stock -{self.sku}"


@dataclass
class StockDeleted(StockEvent):
    sku: str
    shop_id: UUID

    @property
    def description(self):
        return f"Deleted stock -{self.sku}"


@dataclass
class BatchAddedToStock(BatchEvent):
    shop_id: UUID
    sku: str
    batch_ref: str
    quantity: float
    price: float
    stock_time: datetime

    def __post_init__(self):
        super().__post_init__()
        self.stock_time = self.stock_time.timestamp()

    @property
    def description(self):
        return f"Added {self.quantity} units to {self.sku}"


@dataclass
class DispatchedFromStock(StockEvent):
    shop_id: UUID
    sku: str
    quantity: float
    dispatch_time: datetime

    @property
    def description(self):
        return f"Dispatched {self.quantity} units from {self.sku}"


@dataclass
class DispatchedFromBatch(BatchEvent):
    sku: str
    shop_id: UUID
    batch_ref: str
    quantity: int

    @property
    def description(self):
        return f"Dispatched {self.quantity} units from {self.sku}"


@dataclass
class StockSoldOut(StockEvent):
    shop_id: UUID
    sku: str
    when: datetime

    @property
    def description(self):
        return f"Sold out {self.sku}"


@dataclass
class BatchSoldOut(BatchEvent):
    sku: str
    shop_id: UUID
    batch_ref: str
    when: datetime

    @property
    def description(self):
        return f"Sold out {self.sku}"


@dataclass
class UpdatedBatchPrice(BatchEvent):
    sku: str
    shop_id: UUID
    batch_ref: str
    price: str

    @property
    def description(self):
        return f"Updated {self.sku} price to {self.price}"


@dataclass
class AdjustedStockLevel(StockEvent):
    shop_id: UUID
    sku: str
    on: str  # actual batch updated
    by: int
    batch_adjustment_record: list[dict[str, int]]


@dataclass
class IncreasedStockLevel(AdjustedStockLevel):
    @property
    def description(self):
        return f"Increased batch quantity - {self.on} - by - {self.by}"


@dataclass
class DecreasedStockLevel(AdjustedStockLevel):
    @property
    def description(self):
        return f"Decreased batch quantity - {self.on} - by - {self.by}"
