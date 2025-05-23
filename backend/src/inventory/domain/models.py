from __future__ import annotations
from dataclasses import dataclass, InitVar, field
from collections import namedtuple
from datetime import datetime
from enum import Enum
import hashlib
import pytz

from inventory.domain import stock_control
from inventory.domain import events

# from inventory import config

timezone = pytz.timezone("Africa/Lagos")  # config.timezone

Dispatch = namedtuple("Dispatch", "quantity from_")


def sku_generator(name: str, size: MeasurementMetric, product_number: int):
    identifier = f"{name.strip().upper()[:3]}-{size.code}"
    return f"{identifier}-{product_number}"


class OutOfStock(Exception):
    pass


class MeasurementMetric(Enum):
    def __new__(cls, value, code):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.code = code
        return obj

    small = "small", "SM"
    medium = "medium", "MD"
    big = "big", "BG"
    large = "large", "LG"


@dataclass
class Batch:
    sku: str
    ref: str
    stock_in_units: int
    price: float
    stock_time: datetime
    quantity: int = None

    def __post_init__(self):
        if self.quantity is None:
            self.quantity = self.stock_in_units

    def __gt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        if self.stock_time == other.stock_time:
            return self.stock_quantity > other.stock_quantity
        return self.stock_time > other.stock_time

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return stock.stock_time == other.stock_time

    def dispatch(self, quantity: int):
        if self.quantity <= quantity:
            sale = Dispatch(quantity=self.quantity, from_=self.ref)
            self.quantity = 0
        else:
            self.quantity -= quantity
            sale = Dispatch(quantity=quantity, from_=self.ref)
        return sale


@dataclass
class Stock:
    sku: str
    name: str
    metric: MeasurementMetric
    batches: list[Batch] = field(default_factory=list)
    version_number: int = 0
    control_strategy: InitVar[str, None] = None
    offset: int = 0
    last_sale: datetime = None

    def __len__(self):
        return len(self.batches)

    def __iter__(self):
        return (batch for batch in sorted(self.batches) if batch.quantity > 0)

    def __getitem__(self, ref: str):
        "Return batch identified by ref."
        return next(batch for batch in self.batches if batch.ref == ref)

    def __post_init__(self, control_strategy=None):
        if control_strategy:
            self.controller = stock_control.get_controller(self, control_strategy)

    @property
    def level(self):
        return sum(batch.quantity for batch in self)

    @property
    def inventory_value(self):
        return self.controller.compute_inventory_value()

    def set_control_strategy(self, control_strategy: str):
        self.controller = stock_control.get_controller(control_strategy)

    def add(self, ref: str, quantity: float, price: float, timestamp: float):
        time = datetime.fromtimestamp(timestamp, tz=timezone)
        new_batch = Batch(self.sku, ref, quantity, price, time)
        self.batches.append(new_batch)
        self.events.append(
            events.BatchAddedToStock(self.sku, new_batch.ref, quantity, price, time)
        )

    def dispatch(self, quantity: int, timestamp: float):
        dispatch_time = datetime.fromtimestamp(timestamp, tz=timezone)
        if quantity > self.level:
            raise OutOfStock(f"Low Stock Level : Stock<{self.sku}>.")
        dispatch_list = self._dispatch_from_batches_(quantity, dispatch_time)
        self.events.append(
            events.DispatchedFromStock(self.sku, quantity, dispatch_time)
        )
        self.last_sale = dispatch_time
        return dispatch_list

    def _dispatch_from_batches_(self, quantity: int, dispatch_time: datetime):
        dispatch_list = []
        batch_gen = self.controller.dispatch_generator()
        while quantity:
            batch = next(batch_gen)
            if batch.quantity == 0:
                continue
            dispatch = batch.dispatch(quantity)
            quantity -= dispatch.quantity
            dispatch_list.append(dispatch)
        return dispatch_list

    def update_batch(
        self, batch_ref, price: float | None = None, quantity: int | None = None
    ):
        # raises StopIteration if batch not found
        batch = next(batch for batch in self.batches if batch.ref == batch_ref)
        if price:
            batch.price = price
            self.events.append(events.UpdatedBatchPrice(self.sku, batch.ref, price))
        if quantity:
            self.update_batch_quantity(batch, quantity)

    def update_batch_quantity(self, batch, quantity):
        sold = batch.stock_in_units - batch.quantity
        if quantity > batch.stock_in_units:
            offset = quantity - sold
            # Raise stock level
            batch.stock_in_units = quantity
            if batch.quantity > 0:
                # No need for adjustments
                batch.quantity = quantity - sold
            else:
                self.controller.adjust_stock_level(
                    starting_batch=batch, offset=offset, adjustment="raise"
                )
            self.events.append(
                events.IncreasedStockLevel(self.sku, on=batch.ref, by=quantity)
            )
        else:
            offset = (batch.stock_in_units - quantity) - batch.quantity
            # Decrease stock level
            batch.stock_in_units = quantity
            if sold < quantity:
                # no need for adjustments
                batch.quantity = quantity - sold
            else:
                batch.quantity = 0
                self.controller.adjust_stock_level(
                    starting_batch=batch, offset=offset, adjustment="lower"
                )
            self.events.append(
                events.DecreasedStockLevel(self.sku, on=batch.ref, by=quantity)
            )
