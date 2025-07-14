from dataclasses import dataclass, InitVar
from datetime import datetime
from typing import Optional, Any
import uuid

from pydantic import BaseModel, Field, model_serializer, ConfigDict

# from pydantic.dataclasses import dataclass

from inventory.domain import stock_control


class Batch(BaseModel):
    id: int | None = Field(default=None)
    shop_id: uuid.UUID
    sku: str
    ref: str
    price: float
    quantity: int
    stock_time: datetime
    stock_in_units: int


@dataclass
class StockView:
    shop_id: uuid.UUID
    sku: str
    name: str
    last_sale: datetime
    batches: list[Batch]
    id: int | None = None  # Field(default=None)

    def __iter__(self):
        return (batch for batch in self.batches)

    def set_control_strategy(self, control_strategy: str):
        self.controller = stock_control.get_controller(self, control_strategy)

    @property
    def cogs(self):
        return self.controller.compute_cogs(
            start_date=self.batches[0].stock_time, end_date=self.batches[-1].stock_time
        )

    @property
    def value(self):
        return self.controller.compute_inventory_value()

    @property
    def level(self):
        return sum(batch.quantity for batch in self.batches)

    # @model_serializer
    def model_dump(self):
        return {
            "shop_id": self.shop_id,
            "sku": self.sku,
            "name": self.name,
            "last_sale": self.last_sale,
            "batches": [Batch(**batch.__dict__).model_dump() for batch in self.batches],
            "cogs": self.cogs,
            "value": self.value,
            "level": self.level,
        }


class InventoryView(BaseModel):
    shop_id: uuid.UUID
    stocks: list[StockView]

    @property
    def cogs(self):
        return sum(stock.cogs for stock in self.stocks)

    @property
    def value(self):
        return sum(stock.value for stock in self.stocks)

    @model_serializer
    def serialize_model(self):
        return {
            "shop_id": self.shop_id,
            "stocks": [stock.model_dump() for stock in self.stocks],
            "cogs": self.cogs,
            "value": self.value,
        }
