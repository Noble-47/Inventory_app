from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import registry
from pydantic import model_serializer
from sqlmodel import SQLModel, Field, Relationship

from shared import datetime_now_func


class AnalyticModels(SQLModel, registry=registry()):
    def update(self, count, value):
        self.delta = (value - self.value) / self.value
        self.count = self.count
        self.value = value


class Inventory(AnalyticModels, table=True):
    shop_id: UUID = Field(foreign_key="report.shop_id", primary_key=True)
    count: int = Field(default=0.0)
    value: float = Field(default=0.0)
    delta: float = Field(default=0.0)
    cogs: float = Field(default=0.0)

    def update(self, count, value, cogs):
        super().update(count=count, value=value)
        self.cogs = cogs


class Sale(AnalyticModels, table=True):
    shop_id: UUID = Field(foreign_key="report.shop_id", primary_key=True)
    count: int = Field(default=0.0)
    delta: float = Field(default=0.0)
    value: int = Field(default=0.0)


class Order(AnalyticModels, table=True):
    shop_id: UUID = Field(foreign_key="report.shop_id", primary_key=True)
    count: int = Field(default=0.0)
    delta: float = Field(default=0.0)
    value: int = Field(default=0.0)


class Debt(AnalyticModels, table=True):
    shop_id: UUID = Field(foreign_key="report.shop_id", primary_key=True)
    count: float = Field(default=0.0)
    delta: float = Field(default=0.0)
    value: float = Field(default=0.0)


class Analytics(AnalyticModels, table=True):
    __tablename__ = "report"
    shop_id: UUID = Field(primary_key=True)
    inventory: Optional[Inventory] = Relationship()
    debt: Optional[Debt] = Relationship()
    order: Optional[Order] = Relationship()
    sale: Optional[Sale] = Relationship()
    last_updated: Optional[datetime] = Field(default=None)
    profit: float = Field(default=0.0)
    profit_delta: float = Field(default=0.0)

    def insert(self, orders, sales, inventory, debt):
        shop_id = self.shop_id
        self.inventory = Inventory(shop_id=shop_id, **inventory)
        self.order = Order(shop_id=shop_id, **orders)
        self.debt = Debt(shop_id=shop_id, **debt)
        self.sale = Sale(shop_id=shop_id, **sales)
        profit = (self.sale.value - self.inventory.cogs) - self.debt.value
        self.profit_delta = self.compute_profit_delta(profit)
        self.profit = profit
        self.last_updated = datetime_now_func()

    def compute_profit_delta(self, profit):
        if self.profit == 0:
            if profit > self.profit:
                return 100
            if profit < self.profit:
                return -100
            if profit == 0:
                return 0.0
        return (profit - self.profit) / self.profit

    def update(self, orders, sales, inventory, debt):
        if not self.last_updated:
            self.insert(orders, sales, inventory, debt)
            return

        self.inventory.update(**inventory)
        self.order.update(**orders)
        self.debt.update(**debt)
        self.sale.update(**sales)
        profit = (self.sale.value - self.inventory.cogs) - self.debt.value
        self.profit_delta = self.compute_profit_delta(profit)
        self.profit = profit
        self.last_updated = datetime_now_func()

    @model_serializer
    def serialize(self):
        return {
            "shop_id": self.shop_id,
            "inventory": self.inventory.model_dump(),
            "sale": self.sale.model_dump(),
            "debt": self.debt.model_dump(),
            "order": self.order.model_dump(),
            "profit": self.profit,
            "profit_delta": self.profit_delta,
            "last_updated": self.last_updated,
        }
