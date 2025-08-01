from datetime import datetime
from typing import Annotated
from uuid import UUID
import hashlib
import json

from pydantic import BaseModel, Field, PlainSerializer

from shared import datetime_now_func

SerializableUUID = Annotated[
    UUID, PlainSerializer(lambda uid: str(uid), return_type=str)
]


class Event(BaseModel):

    time: datetime = Field(default_factory=datetime_now_func)

    @property
    def event_hash(self):
        model_dump = self.model_dump()
        model_dump["time"] = self.time
        attrs = list(str(v) for k, v in model_dump.items() if k != "description")
        raw = "|".join(attrs).encode()
        return hashlib.sha256(raw).hexdigest()

    @property
    def payload(self):
        data = self.model_dump()
        data.pop("shop_id")
        data.pop("order_id")
        data.pop("time")
        data.pop("description")
        return data

    def serialize(self):
        return {
            "name": self.__class__.__name__,
            "shop_id": self.shop_id,
            "order_id": self.order_id,
            "description": self.description,
            "payload": self.payload,
            "event_hash": self.event_hash,
            "time": self.time,
        }

    def json(self):
        data = self.serialize()
        data["time"] = data["time"].timestamp()
        data["order_id"] = str(data["order_id"])
        data["shop_id"] = str(data["shop_id"])
        for key, value in data["payload"].items():
            if isinstance(value, datetime):
                data["payload"][key] = value.timestamp()
        data["payload"] = json.dumps(data["payload"])
        return data


class OrderLine(BaseModel):
    sku: str
    batch_ref: str
    cost: float


class NewOrderLine(OrderLine):
    expected_quantity: int


class CompletedOrderLine(OrderLine):
    sku: str
    batch_ref: str
    cost: float
    delivered_quantity: int


class OrderCreated(Event):
    shop_id: SerializableUUID
    order_id: SerializableUUID
    status: str
    supplier: str
    supplier_phone: str
    order_line: list[NewOrderLine]
    expected_delivery_date: datetime
    description: str = Field(default="New Order created")


class OrderCompleted(Event):
    order_id: SerializableUUID
    shop_id: SerializableUUID
    orderline: list[CompletedOrderLine]
    delivery_date: datetime
    description: str = Field(default="Order marked as completed.")


class OrderUpdated(Event):
    order_id: SerializableUUID
    shop_id: SerializableUUID
    reason: str = Field(default="None given.")
    updates: str
    description: str = Field(default="Order was updated.")


class OrderCancelled(Event):
    order_id: SerializableUUID
    shop_id: SerializableUUID
    reason: str = Field(default="None given")
    description: str = Field(default="Order cancelled")
