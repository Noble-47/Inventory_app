from __future__ import annotations
from dataclasses import dataclass, InitVar, field
from collections import namedtuple
from datetime import datetime
from typing import ClassVar
from enum import Enum
import hashlib
import pytz

from shared import datetime_now_func

from inventory.exceptions import OutOfStock
from inventory.domain import stock_control
from inventory.domain import events

from inventory.config import TIMEZONE as timezone

Dispatch = namedtuple("Dispatch", "quantity from_")


def sku_generator(name: str):
    identifier = f"{name.strip().upper()}"
    return f"{identifier}"


def manual_batch_ref_generator():
    return f"MANUAL-{datetime_now_func().strftime('%Y%m%d-%H%M%S')}"


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
    shop_id: str
    sku: str
    name: str
    batches: list[Batch] = field(default_factory=list)
    version_number: int = 0
    control_strategy: InitVar[str, None] = None
    offset: int = 0
    last_sale: datetime = None
    events: ClassVar[list] = []

    def __len__(self):
        return len(self.batches)

    def __iter__(self):
        return (batch for batch in sorted(self.batches) if batch.quantity > 0)

    def __getitem__(self, ref: str):
        "Return batch identified by ref."
        return next(batch for batch in self.batches if batch.ref == ref)

    def __hash__(self):
        return hash((self.sku, self.shop_id))

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
        self.controller = stock_control.get_controller(self, control_strategy)

    def add(self, ref: str, quantity: float, price: float, timestamp: float):
        time = datetime.fromtimestamp(timestamp, tz=timezone)
        new_batch = Batch(self.sku, ref, quantity, price, time)
        self.batches.append(new_batch)
        self.events.append(
            events.BatchAddedToStock(
                self.shop_id, self.sku, new_batch.ref, quantity, price, time
            )
        )

    def dispatch(self, quantity: int, timestamp: float):
        dispatch_time = datetime.fromtimestamp(timestamp, tz=timezone)
        if quantity > self.level:
            raise OutOfStock(f"Low Stock Level : Stock<{self.sku}>.")
        dispatch_list = self._dispatch_from_batches_(quantity, dispatch_time)
        self.events.append(
            events.DispatchedFromStock(self.shop_id, self.sku, quantity, dispatch_time)
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
            self.events.append(
                events.DispatchedFromBatch(
                    sku=self.sku,
                    shop_id=self.shop_id,
                    batch_ref=batch.ref,
                    quantity=dispatch.quantity,
                )
            )
            if batch.quantity == 0:
                self.events.append(
                    events.BatchSoldOut(
                        sku=self.sku,
                        shop_id=self.shop_id,
                        batch_ref=batch.ref,
                        when=dispatch_time,
                    )
                )
            dispatch_list.append(dispatch)
        if self.level == 0:
            self.events.append(
                events.StockSoldOut(
                    sku=self.sku, shop_id=self.shop_id, when=dispatch_time
                )
            )
        return dispatch_list

    def get_batch(self, batch_ref):
        try:
            return next(batch for batch in self.batches if batch.ref == batch_ref)
        except StopIteration:
            raise exceptions.BatchNotFound(f"Batch with ref {batch_ref} was not found")

    def update_batch_price(
        self,
        batch_ref,
        price: float,
    ):
        # raises StopIteration if batch not found
        batch = self.get_batch(batch_ref)
        batch.price = price
        self.events.append(
            events.UpdatedBatchPrice(
                sku=self.sku, shop_id=self.shop_id, batch_ref=batch.ref, price=price
            )
        )

    def update_batch_quantity(self, batch_ref, quantity):
        batch = self.get_batch(batch_ref)
        sold = batch.stock_in_units - batch.quantity
        record = []
        if quantity > batch.stock_in_units:
            offset = quantity - sold
            # Raise stock level
            batch.stock_in_units = quantity
            if batch.quantity > 0:
                # No need for adjustments
                batch.quantity = quantity - sold
                record.append({batch.ref: batch.quantity})
            else:
                self.controller.adjust_stock_level(
                    starting_batch=batch,
                    offset=offset,
                    adjustment="raise",
                    record=record,
                )
            self.events.append(
                events.IncreasedStockLevel(
                    self.shop_id,
                    self.sku,
                    on=batch.ref,
                    by=quantity,
                    adjustment_record=record,
                )
            )
        else:
            offset = (batch.stock_in_units - quantity) - batch.quantity
            # Decrease stock level
            batch.stock_in_units = quantity
            if sold < quantity:
                # no need for adjustments
                batch.quantity = quantity - sold
                record.append({batch.ref: batch.quantity})
            else:
                batch.quantity = 0
                self.controller.adjust_stock_level(
                    starting_batch=batch,
                    offset=offset,
                    adjustment="lower",
                    record=record,
                )
            self.events.append(
                events.DecreasedStockLevel(
                    self.shop_id,
                    self.sku,
                    on=batch.ref,
                    by=quantity,
                    adjustment_record=record,
                )
            )
