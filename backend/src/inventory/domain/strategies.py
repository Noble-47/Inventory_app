from __future__ import annotations
from operator import attrgetter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .domain import Batch


class Strategy:
    """
    Defines how inventory value is computed
    and how offsets adjustment is made.
    """

    def get_batch_gen(self, stock: list[Batch]):
        return (batch for batch in stock)

    def calculate_inventory_value(self, stock: list[Batch], stock_level: int):
        batch_gen = self.get_batch_gen(stock)
        inventory_value = 0
        while stock_level:
            batch = next(batch_gen)
            if stock_level >= batch.quantity:
                inventory_value += batch.quantity * batch.price
                stock_level -= batch.quantity
            else:
                inventory_value += stock_level * batch.price
                stock_level = 0
        return inventory_value

    def lower_stock_level(self, offset: int, stock: list[Batch]):
        for batch in stock:
            if batch.quantity == 0:
                continue
            correction_value = min(offset, batch.quantity)
            offset -= correction_value
            batch.quantity -= correction_value
            if offset == 0:
                break
        return offset

    def raise_stock_level(self, offset: int, stock: list[Batch]):
        # batch list is from "batch to be sold from next" backwards
        for batch in stock:
            if batch.quantity == batch.stock_in_units:
                continue
            correction_qty = min(batch.stock_in_units - batch.quantity, offset)
            offset -= correction_qty
            batch.quantity += correction_qty
            if offset == 0:
                break
        return offset


class FIFO(Strategy):
    def get_batch_gen(self, batches: list[Batch]):
        return (batch for batch in sorted(batches, key=attrgetter("stock_time")))


class LIFO(Strategy):
    def get_batch_gen(self, batches: list[Batch]):
        return (
            batch
            for batch in sorted(batches, key=attrgetter("stock_time"), reverse=True)
        )


class WeightedAverage(FIFO):

    def compute_inventory_value(self, batches: list[Batch], stock_level: int):
        batch_gen = self.get_batch_gen(batches)
        weighted_avg_price = sum(
            batch.quantity * batch.price for batch in batches
        ) / sum(batch.quantity for batch in batches)
        return weighted_avg_price * stock_level


class OptimalPrices(Strategy):
    pass


class Greedy(Strategy):
    pass
