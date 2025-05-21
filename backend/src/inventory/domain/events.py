from dataclasses import dataclass
from datetime import datetime


class Event:
    initiated_by: str | None = None

    def event_hash(self):
        pass

    def payload(self):
        return asdict(self)

    def serialize(self):
        return {
            "sku": self.sku,
        }

    def add_initiator(self, username: str):
        self.initiated_by = username


@dataclass
class BatchAddedToStock(Event):
    sku: str
    batch_ref: str
    quantity: float
    price: float
    stock_time: datetime


@dataclass
class DispatchedFromStock(Event):
    sku: str
    quantity: float
    dispatch_time: datetime


@dataclass
class StockSoldOut(Event):
    sku: str
    batch_ref: str
    when: datetime


@dataclass
class UpdatedBatchPrice(Event):
    sku: str
    batch_ref: str
    price: str


@dataclass
class AdjustedStockLevel(Event):
    sku: str
    on: str # actual batch updated
    by: int


@dataclass
class IncreasedStockLevel(AdjustedStockLevel):
    pass


@dataclass
class DecreasedStockLevel(AdjustedStockLevel):
    pass
