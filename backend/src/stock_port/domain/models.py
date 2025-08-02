from datetime import datetime
from uuid import UUID, uuid4
from typing import ClassVar
from enum import Enum

from sqlmodel import SQLModel, Relationship, Field
from pydantic import model_serializer
from sqlalchemy.orm import registry
from sqlalchemy import Sequence

from stock_port import exceptions
from shared import datetime_now_func
from stock_port.domain import events


def batch_ref_gen(sku, quantity):
    ref = f"{sku}-Q{int(quantity)}-{datetime_now_func().strftime('%y-%m-%d-%H-%M')}"
    print(ref)
    return ref


class BaseModel(SQLModel, registry=registry()):
    pass


class ShopSupplier(BaseModel, table=True):
    __tablename__ = "shop_suppliers"
    id: int | None = Field(default=None, primary_key=True)
    shop_id: UUID = Field(foreign_key="records.shop_id")
    supplier_phone: int = Field(foreign_key="suppliers.phone")
    supplier: "Supplier" = Relationship()
    supplies: list["Order"] = Relationship(sa_relationship_kwargs={"viewonly": True})


class Supplier(BaseModel, table=True):
    __tablename__ = "suppliers"
    firstname: str
    lastname: str
    phone: str | None = Field(primary_key=True)
    id: int | None = Field(default=None)
    supplies: list["Order"] = Relationship(
        back_populates="supplier",
        link_model=ShopSupplier,
        sa_relationship_kwargs={"overlaps": "supplier"},
    )

    @model_serializer
    def dump(self):
        return {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "phone": self.phone,
            "supplies": self.supplies,
        }

    def __repr__(self):
        return f"{self.firstname.title()} {self.lastname.title()}"


class OrderStatus(str, Enum):
    pending = "pending"
    delivered = "delivered"
    cancelled = "cancelled"


class BatchLine(BaseModel, table=True):
    batch_ref: str = Field(primary_key=True)
    order_id: UUID = Field(foreign_key="orders.id")
    sku: str
    cost: float
    expected_quantity: int
    delivered_quantity: int | None = Field(default=None)
    delivery_date: datetime | None = Field(default=None)


class Order(BaseModel, table=True):
    __tablename__ = "orders"
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    shop_id: UUID = Field(foreign_key="records.shop_id")
    order_date: datetime = Field(default_factory=datetime_now_func)
    status: OrderStatus = Field(default="pending")
    batchline: list[BatchLine] = Relationship()
    expected_delivery_date: datetime
    delivery_date: datetime | None = Field(default=None)
    cost: float
    supplier_id: int | None = Field(default=None, foreign_key="shop_suppliers.id")
    supplier: Supplier = Relationship(
        back_populates="supplies",
        link_model=ShopSupplier,
        sa_relationship_kwargs={"overlaps": "supplier"},
    )
    supplier_phone: str = Field(foreign_key="suppliers.phone")
    events: ClassVar[list] = []

    def __hash__(self):
        return hash(self.order_date.strftime("%y%m%d%H%M%s"))

    @model_serializer
    def serialize_model(self):
        d = self.__dict__.copy()
        d.pop("_sa_instance_state")
        d["supplier"] = repr(self.supplier)
        return d

    @property
    def expected_products(self):
        return set(batch.sku for batch in self.batchline)

    def process_delivery(self, orderline):
        if not set(orderline.keys()).issubset(self.expected_products):
            raise exceptions.UnprocessableDelivery(
                "Ordered products and delivered products do not match"
            )

        if self.status == OrderStatus.delivered:
            raise exceptions.DuplicateOrderDelivery()

        if self.status == OrderStatus.cancelled:
            raise exceptions.CancelledOrder()

        completed_batchline = []
        for sku in orderline:
            batch = next(batch for batch in self.batchline if batch.sku == sku)
            if batch.delivered_quantity:
                continue
            batch.delivered_quantity = orderline[sku]["quantity"]
            batch.cost = orderline[sku].get("cost", batch.cost)
            batch.delivery_date = datetime_now_func()
            completed_batchline.append(batch.model_dump())

        if all(b.delivered_quantity for b in self.batchline):
            self.status = OrderStatus.delivered
            self.cost = sum(b.cost for b in self.batchline)
        self.delivery_date = datetime_now_func()

        if completed_batchline:
            self.events.append(
                events.OrderCompleted(
                    order_id=self.id,
                    shop_id=self.shop_id,
                    orderline=completed_batchline,
                    delivery_date=self.delivery_date,
                )
            )

    def cancel(self, reason=None):
        self.status = OrderStatus.cancelled
        self.events.append(
            events.OrderCancelled(
                order_id=self.id,
                shop_id=self.shop_id,
                reason=reason,
            )
        )


class Record(BaseModel, table=True):
    __tablename__ = "records"
    shop_id: UUID = Field(primary_key=True)
    deleted: bool = Field(default=False)
    suppliers: list[Supplier] = Relationship(
        link_model=ShopSupplier, sa_relationship_kwargs={"viewonly": True}
    )
    orders: list[Order] = Relationship(sa_relationship_kwargs={"viewonly": True})


class OrderAudit(BaseModel, table=True):
    __tablename__ = "order_audit"
    id: int | None = Field(default=None, primary_key=True)
    shop_id: UUID
    order_id: UUID
    description: str
    time: datetime
    event_hash: str = Field(unique=True)
    payload: str
